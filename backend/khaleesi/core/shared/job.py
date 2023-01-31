"""Job utility"""

# Python.
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TypeVar, Type, Generic, cast

# Django.
from django.conf import settings
from django.core.paginator import Paginator, Page
from django.db import models

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import (
  KhaleesiException,
  MaskingInternalServerException,
  InvalidArgumentException,
)
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import (
  JobExecutionResponse,
  JobCleanupRequest,
  JobExecutionMetadata,
  JobActionConfiguration,
  JobCleanupActionConfiguration,
  User,
)
from khaleesi.proto.core_sawmill_pb2 import Event


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


M = TypeVar('M', bound = models.Model)


class Job(ABC, Generic[M]):
  """A generic job."""

  job             = JobExecutionMetadata()
  action          = JobActionConfiguration()
  items_processed = 0
  start           = datetime.now(tz = timezone.utc)
  job_execution   = JobExecution()
  model    : Type[M]
  paginator: Paginator  # type: ignore[type-arg]

  def __init__(self, *, model: Type[M]) -> None :
    """Initialize the job."""
    self.model = model

  def execute(self, *, request: JobCleanupRequest) -> JobExecutionResponse :
    """Execute the job."""
    self.init(job = request.job, action = request.action_configuration)
    return self.execute_job(job = request.job, action = request.action_configuration)

  def init(self, *,job: JobExecutionMetadata, action: JobActionConfiguration) -> None :
    """Initialize necessary values."""
    if not action.batch_size:
      # Without the batch size, the paginator tries to divide by 0.
      raise InvalidArgumentException(
        public_details  = f'action_configuration.batch_size = {action.batch_size}',
        private_message = 'action_configuration.batch_size is mandatory!',
        private_details = f'action_configuration.batch_size = {action.batch_size}',
      )
    self.start           = datetime.now(tz = timezone.utc)
    self.items_processed = 0
    self.job             = job
    self.action          = action
    self.job_execution   = JobExecution()
    self.paginator       = Paginator(self.get_queryset(), action.batch_size)

  def execute_job(
      self, *,
      job   : JobExecutionMetadata,
      action: JobActionConfiguration,
  ) -> JobExecutionResponse :
    """The main method."""
    # Start job execution.
    LOGGER.info('Attempting to start job.')
    try:
      self.job_execution = JobExecution.objects.start_job_execution(job = job)
    except Exception as exception:
      self._log_event(
        action  = Event.Action.ActionType.START,
        result  = Event.Action.ResultType.FATAL,
        details = 'Job failed to start.',
      )
      self._handle_fatal_exception(exception = exception, details = 'Job failed to start.')
      raise
    self._log_event(
      action  = Event.Action.ActionType.START,
      result  = Event.Action.ResultType.SUCCESS,
      details = 'Job started.',
    )

    # Determine if skipping happens.
    if not self.job_execution.in_progress:
      self._log_event(
        action  = Event.Action.ActionType.END,
        result  = Event.Action.ResultType.WARNING,
        details = 'Job skipped because a different job execution is in progress.',
      )
      self.job_execution.finish(
        status          = JobExecutionResponse.SKIPPED,
        items_processed = self.items_processed,
        details         = 'Job skipped because a different job execution is in progress.',
      )
      return self.job_execution.to_grpc_job_execution_response()
    LOGGER.info('Job is not getting skipped.')


    # Determine total amount of affected items.
    try:
      total = self.paginator.count
      LOGGER.info(f'The total amount of affected items is {total}.')
      self.job_execution.set_total(total = total)
    except Exception as exception:  # pylint: disable=broad-except
      self._handle_fatal_exception(
        exception = exception,
        details   = 'Could not determine total amount of affected items.',
      )
      return self.job_execution.to_grpc_job_execution_response()
    self.job_execution.set_total(total = total)

    # Execute loop.
    try:
      for page_number in self.paginator.page_range:
        # Timeout check.
        if datetime.now(tz = timezone.utc) > \
            self.start + action.timelimit.ToTimedelta():
          self.job_execution.finish(
            status          = JobExecutionResponse.Status.TIMEOUT,
            items_processed = self.items_processed,
            details         = 'Job timed out.',
          )
          self._log_event(
            action  = Event.Action.ActionType.END,
            result  = Event.Action.ResultType.WARNING,
            details = 'Job timed out.'
          )
          return self.job_execution.to_grpc_job_execution_response()

        # Execute loop.
        LOGGER.info('Executing next batch.')
        self.items_processed += self.execute_batch(page = self.get_page(page_number = page_number))
        LOGGER.info(f'{self.items_processed} items processed so far.')

      # Job is done.
      self.job_execution.finish(
        status          = JobExecutionResponse.Status.SUCCESS,
        items_processed = self.items_processed,
        details         = 'Job finished successfully.',
      )
      self._log_event(
        action  = Event.Action.ActionType.END,
        result  = Event.Action.ResultType.SUCCESS,
        details = 'Job finished successfully.'
      )
      return self.job_execution.to_grpc_job_execution_response()

    except Exception as exception:  # pylint: disable=broad-except
      self._handle_error_exception(
        exception = MaskingInternalServerException(exception = exception),
        details   = 'Exception happened during job execution.',
      )
      return self.job_execution.to_grpc_job_execution_response()

  def get_page(self, *, page_number: int) -> Page[M] :
    """Get the next page to be worked on."""
    return self.paginator.get_page(page_number)

  @abstractmethod
  def execute_batch(self, *, page: Page[M]) -> int :
    """Execute one batch of the job and return the number of items that were processed."""

  @abstractmethod
  def get_queryset(self) -> models.QuerySet[M] :
    """Return the full queryset to be iterated over."""

  def target(self) -> str :
    """Return the target resource. By default, this is should be the affected model name."""
    return self.model.__name__

  def target_type(self) -> str :
    """Return the target resource type. By default, this is table."""
    return khaleesi_settings['BATCH']['TARGET_TYPE']

  def owner(self) -> User :
    """Return the owner of the target resources. By default, this is the service."""
    owner = User()
    owner.id = f'{khaleesi_settings["METADATA"]["GATE"]}-{khaleesi_settings["METADATA"]["SERVICE"]}'
    owner.type = User.UserType.SYSTEM
    return owner

  def _handle_fatal_exception(self, *, exception: Exception, details: str) -> None :
    """Handle exceptions during job execution."""
    self._handle_error_exception(
      exception    = exception,
      details      = details,
      event_result = Event.Action.ResultType.FATAL,
    )

  def _handle_error_exception(
      self, *,
      exception   : Exception,
      details     : str,
      event_result: 'Event.Action.ResultType.V' = Event.Action.ResultType.ERROR,
  ) -> None :
    """Handle exceptions during job execution."""
    khaleesi_exception: KhaleesiException
    if isinstance(exception, KhaleesiException):
      khaleesi_exception = exception
    else:
      khaleesi_exception = MaskingInternalServerException(exception = exception)

    self.job_execution.finish(
      status          = JobExecutionResponse.Status.ERROR,
      items_processed = self.items_processed,
      details         = details,
    )
    self._log_event(
      action  = Event.Action.ActionType.END,
      result  = event_result,
      details = details,
    )
    SINGLETON.structured_logger.log_error(exception = khaleesi_exception)

  def _log_event(
      self, *,
      action : 'Event.Action.ActionType.V',
      result : 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log start and end events."""
    SINGLETON.structured_logger.log_event(
      target      = self.target(),
      target_type = self.target_type(),
      owner       = self.owner(),
      action      = '',  # Batch jobs use START and END crud types.
      action_crud = action,
      result      = result,
      details     = f'Job execution "{self.job.execution_id}" for "{self.job.job_id}": '
                    f'{details}. {self.items_processed} items processed so far.',
    )


# noinspection PyAbstractClass
class CleanupJob(Job, Generic[M]):  # type: ignore[type-arg]
  """Job specifically for cleaning up."""

  cleanup_configuration = JobCleanupActionConfiguration()
  cleanup_timestamp = datetime.now(tz = timezone.utc)

  def execute_batch(self, *, page: Page[M]) -> int :
    """Execute a batch deletion."""
    count, _ = self.model.objects.filter(
      pk__in = models.Subquery(page.object_list.values('pk')),  # type: ignore[attr-defined]
    ).delete()
    return cast(int, count)

  def execute(self, *, request: JobCleanupRequest) -> JobExecutionResponse :
    """Execute the job."""
    self.init(job = request.job, action = request.action_configuration)
    self.init_cleanup(cleanup = request.cleanup_configuration)
    return self.execute_job(job = request.job, action = request.action_configuration)

  def init_cleanup(self, *, cleanup: JobCleanupActionConfiguration) -> None :
    """Initialize necessary values."""
    self.cleanup_configuration = cleanup
    self.cleanup_timestamp = self.start - cleanup.cleanup_delay.ToTimedelta()

  def get_page(self, *, page_number: int) -> Page[M] :
    """Get the next page to be worked on."""
    # Since the data gets deleted, we continue with the next first page.
    return self.paginator.get_page(1)  # 1-based index.
