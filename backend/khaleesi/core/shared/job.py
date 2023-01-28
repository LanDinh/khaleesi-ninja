"""Job utility"""

# Python.
from abc import ABC, abstractmethod
from datetime import datetime

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobCleanupRequest, User
from khaleesi.proto.core_sawmill_pb2 import Event


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Job(ABC):
  """A generic job."""

  request         = JobCleanupRequest()
  job_execution   = JobExecution()
  items_processed = 0

  def execute(self, *, request: JobCleanupRequest) -> JobExecutionResponse :
    """The main method."""
    # Start job execution.
    LOGGER.info('Attempting to start job.')
    start = datetime.now()
    try:
      self.request         = request
      self.items_processed = 0
      self.job_execution   = JobExecution.objects.start_job_execution(job = request.job)
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
      total = self.count_total()
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
      while True:
        # Timeout check.
        if datetime.now() > start + request.action_configuration.timelimit.ToTimedelta():
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

        # Job is done.
        if self.items_processed >= total:
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

        # Execute loop.
        LOGGER.info('Executing next batch.')
        self.items_processed += self.execute_batch()
        LOGGER.info(f'{self.items_processed} items processed so far.')

    except Exception as exception:  # pylint: disable=broad-except
      self._handle_error_exception(
        exception = MaskingInternalServerException(exception = exception),
        details   = 'Exception happened during job execution.',
      )
      return self.job_execution.to_grpc_job_execution_response()

  @abstractmethod
  def execute_batch(self) -> int :
    """Execute one batch of the job and return the number of items that were processed."""

  @abstractmethod
  def count_total(self) -> int :
    """Count the total number of items that should be executed."""

  @abstractmethod
  def target(self) -> str :
    """Return the target resource. By default, this is should be the affected model name."""

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
      details     = f'Job execution "{self.request.job.execution_id}" '\
                    f'for "{self.request.job.job_id}": '
                    f'{details}. {self.items_processed} items processed so far.',
    )
