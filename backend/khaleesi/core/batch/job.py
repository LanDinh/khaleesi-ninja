"""Job utility"""

# Python.
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from threading import Event as ThreadingEvent
from typing import TypeVar, Type, Generic

# Django.
from django.conf import settings
from django.core.paginator import Paginator, Page
from django.db import models

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
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
  JobRequest,
  JobExecutionMetadata,
  JobActionConfiguration,
  JobCleanupActionConfiguration,
  User,
)
from khaleesi.proto.core_sawmill_pb2 import Event


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


M = TypeVar('M', bound = models.Model)


class BaseJob(ABC, Generic[M]):
  """Generic job logic."""

  job            = JobExecutionMetadata()
  action         = JobActionConfiguration()
  itemsProcessed = 0
  start          = datetime.now(tz = timezone.utc)
  jobExecution   = JobExecution()
  model    : Type[M]
  paginator: Paginator  # type: ignore[type-arg]

  def __init__(
      self, *,
      model : Type[M],
      job   : JobExecutionMetadata,
      action: JobActionConfiguration,
  ) -> None :
    """Initialize the job."""
    self.model = model
    if not action.batchSize:
      # Without the batch size, the paginator tries to divide by 0.
      raise InvalidArgumentException(
        publicDetails  = f'actionConfiguration.batchSize = {action.batchSize}',
        privateMessage = 'actionConfiguration.batchSize is mandatory!',
        privateDetails = f'actionConfiguration.batchSize = {action.batchSize}',
      )
    if not action.timelimit.ToNanoseconds() > 0:
      # Without the time limit, the job will not run at all.
      raise InvalidArgumentException(
        publicDetails  = f'actionConfiguration.timelimit = {action.timelimit}',
        privateMessage = 'actionConfiguration.timelimit is mandatory!',
        privateDetails = f'actionConfiguration.timelimit = {action.timelimit}',
      )
    self.start          = datetime.now(tz = timezone.utc)
    self.itemsProcessed = 0
    self.job            = job
    self.action         = action
    self.jobExecution   = JobExecution()

  def execute(self, *, stopEvent: ThreadingEvent) -> JobExecutionResponse :
    """Execute the job."""
    # Start job execution.
    LOGGER.info(f'{self._loggingPrefix()} Attempting to start.')
    self.paginator = Paginator(self.getQueryset(), self.action.batchSize)
    try:
      self.jobExecution = JobExecution.objects.startJobExecution(job = self.job)
    except Exception as exception:
      LOGGER.fatal(f'{self._loggingPrefix()} Failed to start.')
      self._logEvent(
        action  = Event.Action.ActionType.START,
        result  = Event.Action.ResultType.FATAL,
        details = 'Job failed to start.',
      )
      self._handleFatalException(exception = exception, details = 'Job failed to start.')
      raise
    self._logEvent(
      action  = Event.Action.ActionType.START,
      result  = Event.Action.ResultType.SUCCESS,
      details = 'Job started.',
    )

    # Determine if skipping happens.
    if not self.jobExecution.inProgress:
      self._handleJobEnd(
        details         = 'Job skipped because a different job execution is in progress.',
        executionStatus = JobExecutionResponse.Status.SKIPPED,
      )
      return self.jobExecution.toGrpc()
    LOGGER.info(f'{self._loggingPrefix()} Job not getting skipped.')


    # Determine total amount of affected items.
    try:
      total = self.paginator.count
      LOGGER.info(f'{self._loggingPrefix()} The total amount of affected items is {total}.')
      self.jobExecution.setTotal(total = total)
    except Exception as exception:  # pylint: disable=broad-except
      self._handleFatalException(
        exception = exception,
        details   = 'Could not determine total amount of affected items.',
      )
      return self.jobExecution.toGrpc()
    self.jobExecution.setTotal(total = total)

    # Execute loop.
    try:
      for pageNumber in self.paginator.page_range:
        # Abort check.
        if stopEvent.is_set():
          self._handleJobEnd(
            details         = 'Job aborted.',
            executionStatus = JobExecutionResponse.Status.ABORT,
          )
          return self.jobExecution.toGrpc()
        # Timeout check.
        if datetime.now(tz = timezone.utc) > \
            self.start + self.action.timelimit.ToTimedelta():
          self._handleJobEnd(
            details         = 'Job timed out.',
            executionStatus = JobExecutionResponse.Status.TIMEOUT,
          )
          return self.jobExecution.toGrpc()

        # Execute loop.
        LOGGER.info(f'{self._loggingPrefix()} Executing next batch.')
        self.itemsProcessed += self.executeBatch(page = self.getPage(pageNumber = pageNumber))
        LOGGER.info(f'{self._loggingPrefix()} {self.itemsProcessed} items processed so far.')

      # Job is done.
      self._handleJobEnd(
        details         = 'Job finished successfully.',
        executionStatus = JobExecutionResponse.Status.SUCCESS,
        eventResult     = Event.Action.ResultType.SUCCESS,
      )
      return self.jobExecution.toGrpc()

    except Exception as exception:  # pylint: disable=broad-except
      self._handleErrorException(
        exception = MaskingInternalServerException(exception = exception),
        details   = 'Exception happened during job execution.',
      )
      return self.jobExecution.toGrpc()

  def getPage(self, *, pageNumber: int) -> Page[M] :
    """Get the next page to be worked on."""
    return self.paginator.get_page(pageNumber)

  @abstractmethod
  def executeBatch(self, *, page: Page[M]) -> int :
    """Execute one batch of the job and return the number of items that were processed."""

  @abstractmethod
  def getQueryset(self) -> models.QuerySet[M] :
    """Return the full queryset to be iterated over."""

  def target(self) -> str :
    """Return the target resource. By default, this is should be the affected model name."""
    return self.model.__name__

  def targetType(self) -> str :
    """Return the target resource type. By default, this is table."""
    return khaleesiSettings['BATCH']['TARGET_TYPE']

  def owner(self) -> User :
    """Return the owner of the target resources. By default, this is the service."""
    owner = User()
    owner.id   = f'{khaleesiSettings["METADATA"]["GATE"]}-{khaleesiSettings["METADATA"]["SERVICE"]}'
    owner.type = User.UserType.SYSTEM
    return owner

  def _handleFatalException(self, *, exception: Exception, details: str) -> None :
    """Handle exceptions during job execution."""
    self._handleErrorException(
      exception   = exception,
      details     = details,
      eventResult = Event.Action.ResultType.FATAL,
    )

  def _handleErrorException(
      self, *,
      exception  : Exception,
      details    : str,
      eventResult: 'Event.Action.ResultType.V' = Event.Action.ResultType.ERROR,
  ) -> None :
    """Handle exceptions during job execution."""
    khaleesiException: KhaleesiException
    if isinstance(exception, KhaleesiException):
      khaleesiException = exception
    else:
      khaleesiException = MaskingInternalServerException(exception = exception)
    self._handleJobEnd(
      details         = details,
      executionStatus = JobExecutionResponse.Status.ERROR,
      eventResult     = eventResult,
    )
    SINGLETON.structuredLogger.logError(exception = khaleesiException)

  def _handleJobEnd(
      self, *,
      details        : str,
      executionStatus: 'JobExecutionResponse.Status.V',
      eventResult    : 'Event.Action.ResultType.V' = Event.Action.ResultType.WARNING,
  ) -> None :
    """Handle the job finishing."""
    if eventResult == Event.Action.ResultType.WARNING:
      LOGGER.warning(f'{self._loggingPrefix()} {details}')
    elif eventResult == Event.Action.ResultType.ERROR:
      LOGGER.error(f'{self._loggingPrefix()} {details}')
    elif eventResult == Event.Action.ResultType.FATAL:
      LOGGER.fatal(f'{self._loggingPrefix()} {details}')

    self.jobExecution.finish(
      status         = executionStatus,
      itemsProcessed = self.itemsProcessed,
      details        = details,
    )
    self._logEvent(
      action  = Event.Action.ActionType.END,
      result  = eventResult,
      details = details,
    )

  def _logEvent(
      self, *,
      action : 'Event.Action.ActionType.V',
      result : 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log start and end events."""
    SINGLETON.structuredLogger.logEvent(
      target     = self.target(),
      targetType = self.targetType(),
      owner      = self.owner(),
      action     = '',  # Batch jobs use START and END crud types.
      actionCrud = action,
      result     = result,
      details    = f'{self._loggingPrefix()} '
                   f'{details} {self.itemsProcessed} items processed so far.',
    )

  def _loggingPrefix(self) -> str :
    """Return uniform logging prefix."""
    return f'Job execution "{self.job.executionId}" for "{self.job.jobId}":'

# noinspection PyAbstractClass
class Job(BaseJob[M], Generic[M]):
  """General job."""

  def __init__(self, *, model: Type[M], request : JobRequest) -> None :
    """Initialize the job."""
    super().__init__(model = model, job = request.job, action = request.actionConfiguration)


# noinspection PyAbstractClass
class CleanupJob(BaseJob[M], Generic[M]):
  """Job specifically for cleaning up."""

  cleanupConfiguration = JobCleanupActionConfiguration()
  cleanupTimestamp     = datetime.now(tz = timezone.utc)

  def __init__(self, *, model: Type[M], request : JobRequest) -> None :
    """Initialize the job."""
    super().__init__(model = model, job = request.job, action = request.actionConfiguration)

    cleanup = request.cleanupConfiguration

    if not cleanup.isCleanupJob:
      # Without the cleanup configuration, the job will not run at all.
      raise InvalidArgumentException(
        publicDetails  = f'cleanupConfiguration = {cleanup}',
        privateMessage = 'cleanupConfiguration is mandatory!',
        privateDetails = f'cleanupConfiguration = {cleanup}',
      )

    self.cleanupConfiguration = cleanup
    self.cleanupTimestamp     = self.start - cleanup.cleanupDelay.ToTimedelta()

  def executeBatch(self, *, page: Page[M]) -> int :
    """Execute a batch deletion."""
    count, _ = self.getQueryset().filter(
      pk__in = models.Subquery(page.object_list.values('pk')),  # type: ignore[attr-defined]
    ).delete()
    return count

  def getPage(self, *, pageNumber: int) -> Page[M] :
    """Get the next page to be worked on."""
    # Since the data gets deleted, we continue with the next first page.
    return self.paginator.get_page(1)  # 1-based index.
