"""Job utility"""

# Python.
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from threading import Event as ThreadingEvent
from typing import TypeVar, Type, Generic

# Django.
from django.conf import settings
from django.core.paginator import Paginator, Page
from django.db import models, transaction

# gRPC.
from google.protobuf.json_format import MessageToJson

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import (
  KhaleesiException,
  MaskingInternalServerException,
  InvalidArgumentException,
)
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.models.jobExecution import JobExecution as DbJobExecution
from khaleesi.proto.core_pb2 import (
  JobExecution as GrpcJobExecution,
  JobExecutionRequest,
  User,
)
from khaleesi.proto.core_sawmill_pb2 import Event


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


M = TypeVar('M', bound = models.Model)


class BaseJob(ABC, Generic[M]):
  """Generic job logic."""

  model         : Type[M]
  start         : datetime
  request       : GrpcJobExecution
  itemsProcessed: int
  jobExecution  : DbJobExecution
  paginator     : Paginator  # type: ignore[type-arg]

  def __init__(self, *, model: Type[M], request: JobExecutionRequest) -> None :
    """Initialize the job."""

    action = request.jobExecution.actionConfiguration

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
    self.model          = model
    self.start          = datetime.now(tz = timezone.utc)
    self.itemsProcessed = 0
    self.request        = request.jobExecution

  def execute(self, *, stopEvent: ThreadingEvent) -> None :
    """Execute the job."""
    # Start job execution.
    LOGGER.info(f'{self._loggingPrefix()} Attempting to start.')
    self.paginator = Paginator(self.getQueryset(), self.request.actionConfiguration.batchSize)

    self._startJobExecution()

    if self._checkIfJobGetsSkipped() or self._checkIfTotalAmountOfItemsIsCalculated():
      return

    # Execute loop.
    try:
      for pageNumber in self.paginator.page_range:
        if self._checkIfAborted(stopEvent = stopEvent) or self._checkTimeout():
          return

        # Execute loop.
        LOGGER.info(f'{self._loggingPrefix()} Executing next batch.')
        self.itemsProcessed += self.executeBatch(page = self.getPage(pageNumber = pageNumber))
        LOGGER.info(f'{self._loggingPrefix()} {self.itemsProcessed} items processed so far.')

      # Job is done.
      self._handleJobEnd(
        details         = 'Job finished successfully.',
        executionStatus = GrpcJobExecution.Status.SUCCESS,
        eventResult     = Event.Action.ResultType.SUCCESS,
      )
      return

    except Exception as exception:  # pylint: disable=broad-except
      self._handleErrorException(
        exception = MaskingInternalServerException(exception = exception),
        details   = 'Exception happened during job execution.',
      )
      return

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
      executionStatus = GrpcJobExecution.Status.ERROR,
      eventResult     = eventResult,
    )
    SINGLETON.structuredLogger.logError(exception = khaleesiException)

  def _handleJobEnd(
      self, *,
      details        : str,
      executionStatus: 'GrpcJobExecution.Status.V',
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
      statusDetails  = details,
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
    event = Event()
    event.target.id   = self.target()
    event.target.type = self.targetType()
    event.target.owner.CopyFrom(self.owner())
    event.action.crudType = action
    event.action.result   = result
    event.action.details  = f'{self._loggingPrefix()} '\
                            f'{details} {self.itemsProcessed} items processed so far.'
    SINGLETON.structuredLogger.logEvent(event = event)

  def _loggingPrefix(self) -> str :
    """Return uniform logging prefix."""
    return f'Job execution "{self.request.executionMetadata.id}" '\
           f'for "{self.request.jobMetadata.id}":'

  def _startJobExecution(self) -> None :
    """Start job execution. Returns false when job is getting skipped."""
    try:
      with transaction.atomic(using = 'write'):
        self.request.status = GrpcJobExecution.Status.IN_PROGRESS
        if DbJobExecution.objects.countJobsInProgress(job = self.request.jobMetadata) > 0:
          self.request.status = GrpcJobExecution.Status.SKIPPED
        self.jobExecution = DbJobExecution.objects.khaleesiCreate(grpc = self.request)
    except Exception as exception:
      LOGGER.fatal(f'{self._loggingPrefix()} Failed to start.')
      self.jobExecution = DbJobExecution()
      self.jobExecution.fromGrpc(grpc = self.request)
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

  def _checkIfJobGetsSkipped(self) -> bool:
    """Check if the job gets skipped because there is already an instance of it running."""
    if not self.jobExecution.inProgress:
      self._handleJobEnd(
        details         = 'Job skipped because a different job execution is in progress.',
        executionStatus = GrpcJobExecution.Status.SKIPPED,
      )
      return True
    LOGGER.info(f'{self._loggingPrefix()} Job not getting skipped.')
    return False

  def _checkIfTotalAmountOfItemsIsCalculated(self) -> bool :
    """Determine the total amount of items if possible."""
    try:
      total = self.paginator.count
      LOGGER.info(f'{self._loggingPrefix()} The total amount of affected items is {total}.')
      self.jobExecution.setTotal(total = total)
    except Exception as exception:  # pylint: disable=broad-except
      self._handleFatalException(
        exception = exception,
        details   = 'Could not determine total amount of affected items.',
      )
      return True
    self.jobExecution.setTotal(total = total)
    return False

  def _checkIfAborted(self, *, stopEvent: ThreadingEvent) -> bool :
    """Check if the job got aborted."""
    if stopEvent.is_set():
      self._handleJobEnd(
        details         = 'Job aborted.',
        executionStatus = GrpcJobExecution.Status.ABORT,
      )
      return True
    return False
  def _checkTimeout(self) -> bool :
    """Check if the job timed out."""
    if datetime.now(tz = timezone.utc) > \
        self.start + self.request.actionConfiguration.timelimit.ToTimedelta():
      self._handleJobEnd(
        details         = 'Job timed out.',
        executionStatus = GrpcJobExecution.Status.TIMEOUT,
      )
      return True
    return False

# noinspection PyAbstractClass
class Job(BaseJob[M], Generic[M]):
  """General job."""


# noinspection PyAbstractClass
class CleanupJob(BaseJob[M], Generic[M]):
  """Job specifically for cleaning up."""

  def __init__(self, *, model: Type[M], request : JobExecutionRequest) -> None :
    """Initialize the job."""
    super().__init__(model = model, request = request)

    cleanup = request.jobExecution.cleanupConfiguration

    if not cleanup.isCleanupJob:
      # Without the cleanup configuration, the job will not run at all.
      raise InvalidArgumentException(
        publicDetails  = f'cleanupConfiguration = {MessageToJson(cleanup)}',
        privateMessage = 'cleanupConfiguration is mandatory!',
        privateDetails = f'cleanupConfiguration = {MessageToJson(cleanup)}',
      )

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
