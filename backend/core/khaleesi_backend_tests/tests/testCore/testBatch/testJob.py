"""Test job execution."""

# Python.
from threading import Event
from unittest.mock import patch, MagicMock, PropertyMock

# Django.
from django.core.paginator import Page
from django.db.models import QuerySet

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.batch.job import Job as BaseJob, CleanupJob as BaseCleanupJob
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.models.jobExecution import JobExecution as DbJobExecution
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution, JobExecutionRequest


class Job(BaseJob[DbJobExecution]):
  """Test job for testing."""

  mock = MagicMock()

  def executeBatch(self, *, page: Page[DbJobExecution]) -> int :
    """Execute one batch of the job and return the number of items that were processed."""
    self.mock.executeBatch()
    return 2

  def getQueryset(self) -> QuerySet[DbJobExecution] :
    """Return the full queryset to be iterated over."""
    return self.mock.getQueryset()  # type: ignore[no-any-return]

  def finishJob(self) -> None :
    """Finish up."""
    self.mock.finish()  # pylint: disable=no-value-for-parameter


class CleanupJob(BaseCleanupJob[DbJobExecution]):
  """Test job for testing."""

  mock = MagicMock()

  def getQueryset(self) -> QuerySet[DbJobExecution] :
    """Return the full queryset to be iterated over."""
    return self.mock.getQueryset()  # type: ignore[no-any-return]


class JobTestMixin:
  """Common methods for all job tests."""

  def _successfullyStartJob(
      self, *,
      start    : MagicMock,
      paginator: MagicMock,
  ) -> JobExecutionRequest :
    """Prepare successful job start"""
    jobExecution = MagicMock()
    def setTotal(total: int) -> None :
      jobExecution.totalItems = total
    def finish(
        status        : 'GrpcJobExecution.Status.V',
        itemsProcessed: int,
        statusDetails : str,
    ) -> None :
      jobExecution.status         = GrpcJobExecution.Status.Name(status)
      jobExecution.itemsProcessed = itemsProcessed
      jobExecution.statusDetails  = statusDetails
    jobExecution.inProcess = True
    jobExecution.setTotal  = setTotal
    jobExecution.finish    = finish
    start.objects.khaleesiCreate.return_value = jobExecution
    start.objects.countJobExecutionsInProgress.return_value = 0
    paginator.return_value.count = 6
    paginator.return_value.page_range = [ 1, 2, 3 ]
    request = JobExecutionRequest()
    request.jobExecution.configuration.action.batchSize = 2
    request.jobExecution.configuration.action.timelimit.FromSeconds(60)
    return request


@patch('khaleesi.core.models.baseModel.transaction')
@patch('khaleesi.core.batch.job.LOGGER')
@patch('khaleesi.core.batch.job.transaction')
@patch('khaleesi.core.batch.job.Paginator')
@patch('khaleesi.core.batch.job.SINGLETON')
@patch('khaleesi.core.batch.job.DbJobExecution')
class JobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job: Job

  def _setJob(self, *, request: JobExecutionRequest) -> None :
    self.job = Job(model = DbJobExecution, request = request)
    self.job.mock = MagicMock()

  def testMandatoryBatchSize(self, *_: MagicMock) -> None :
    """Test that the batch size is specified."""
    # Execute test.
    with self.assertRaises(InvalidArgumentException) as context:
      self.job = Job(model = DbJobExecution, request = JobExecutionRequest())
    # Assert result.
    self.assertIn('configuration.action.batchSize', context.exception.publicDetails)
    self.assertIn('configuration.action.batchSize', context.exception.privateMessage)
    self.assertIn('configuration.action.batchSize', context.exception.privateDetails)

  def testMandatoryTimeLimit(self, *_: MagicMock) -> None :
    """Test that the timelimit is specified."""
    # Execute test.
    with self.assertRaises(InvalidArgumentException) as context:
      request = JobExecutionRequest()
      request.jobExecution.configuration.action.batchSize = 5
      self.job = Job(model = DbJobExecution, request = request)
    # Assert result.
    self.assertIn('configuration.action.timelimit', context.exception.publicDetails)
    self.assertIn('configuration.action.timelimit', context.exception.privateMessage)
    self.assertIn('configuration.action.timelimit', context.exception.privateDetails)

  def testJobFailsToStart(self, start: MagicMock, singleton: MagicMock, *_: MagicMock) -> None :
    """Test failure for the job to start."""
    # Prepare data.
    start.objects.countJobExecutionsInProgress.side_effect = Exception('start failure')
    start.return_value = MagicMock()
    request = JobExecutionRequest()
    request.jobExecution.configuration.action.batchSize = 2
    request.jobExecution.configuration.action.timelimit.FromSeconds(60)
    self._setJob(request = request)
    # Execute test.
    with self.assertRaises(Exception):
      self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    singleton.structuredLogger.logError.assert_called_once()
    self.job.mock.finish.assert_called_once()  # pylint: disable=no-member

  # noinspection PyUnusedLocal
  def testJobIsSkipped(self, start: MagicMock, singleton: MagicMock, *_: MagicMock) -> None :
    """Test job getting skipped."""
    # Prepare data.
    start.objects.countJobExecutionsInProgress.return_value = 1337
    request = JobExecutionRequest()
    request.jobExecution.configuration.action.batchSize = 2
    request.jobExecution.configuration.action.timelimit.FromSeconds(60)
    self._setJob(request = request)
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(GrpcJobExecution.Status.SKIPPED, self.job.request.status)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    self.job.mock.finish.assert_called_once()  # pylint: disable=no-member

  def testJobFailedToGetCount(self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test failure for the job to get the total count."""
    # Prepare data.
    request = self._successfullyStartJob(start = start, paginator = paginator)
    type(paginator.return_value).count = PropertyMock(side_effect = Exception('no total count'))
    self._setJob(request = request)
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(
      GrpcJobExecution.Status.Name(GrpcJobExecution.Status.ERROR),
      self.job.jobExecution.status,
    )
    self.assertEqual(0                            , self.job.jobExecution.itemsProcessed)
    self.assertIn('total amount of affected items', self.job.jobExecution.statusDetails)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    singleton.structuredLogger.logError.assert_called_once()
    self.job.mock.finish.assert_called_once()  # pylint: disable=no-member

  def testJobAbort(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test job timeout."""
    # Prepare data.
    request = self._successfullyStartJob(start = start, paginator = paginator)
    self._setJob(request = request)
    stopEvent = Event()
    stopEvent.set()
    # Execute test.
    self.job.execute(stopEvent = stopEvent)
    # Assert result.
    self.assertIn('aborted', self.job.jobExecution.statusDetails)
    self.assertEqual(
      GrpcJobExecution.Status.Name(GrpcJobExecution.Status.ABORT),
      self.job.jobExecution.status,
    )
    self.assertEqual(0, self.job.jobExecution.itemsProcessed)
    self.assertEqual(6, self.job.jobExecution.totalItems)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    self.job.mock.finish.assert_called_once()  # pylint: disable=no-member

  def testJobTimeout(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test job timeout."""
    # Prepare data.
    request = self._successfullyStartJob(start = start, paginator = paginator)
    request.jobExecution.configuration.action.timelimit.FromNanoseconds(1)
    self._setJob(request = request)
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertIn('timed out', self.job.jobExecution.statusDetails)
    self.assertEqual(
      GrpcJobExecution.Status.Name(GrpcJobExecution.Status.TIMEOUT),
      self.job.jobExecution.status,
    )
    self.assertEqual(0, self.job.jobExecution.itemsProcessed)
    self.assertEqual(6, self.job.jobExecution.totalItems)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    self.job.mock.finish.assert_called_once()  # pylint: disable=no-member

  def testJobError(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test job error during batch processing."""
    # Prepare data.
    request = self._successfullyStartJob(start = start, paginator = paginator)
    self._setJob(request = request)
    self.job.mock.executeBatch.side_effect = Exception('error in batch')
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(
      GrpcJobExecution.Status.Name(GrpcJobExecution.Status.ERROR),
      self.job.jobExecution.status,
    )
    self.assertEqual(0       , self.job.jobExecution.itemsProcessed)
    self.assertEqual(6       , self.job.jobExecution.totalItems)
    self.assertIn('Exception', self.job.jobExecution.statusDetails)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    singleton.structuredLogger.logError.assert_called_once()
    self.job.mock.executeBatch.assert_called_once_with()
    self.job.mock.finish.assert_called_once()  # pylint: disable=no-member

  def testJobSuccess(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test successful job run."""
    # Prepare data.
    request = self._successfullyStartJob(start = start, paginator = paginator)
    self._setJob(request = request)
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(
      GrpcJobExecution.Status.Name(GrpcJobExecution.Status.SUCCESS),
      self.job.jobExecution.status,
    )
    self.assertEqual(6          , self.job.jobExecution.totalItems)
    self.assertEqual(6          , self.job.jobExecution.itemsProcessed)
    self.assertIn('successfully', self.job.jobExecution.statusDetails)
    self.assertEqual(2          , singleton.structuredLogger.logEvent.call_count)
    self.assertEqual(3          , self.job.mock.executeBatch.call_count)
    self.assertNotEqual(1       , paginator.return_value.get_page.call_args.args[0])
    self.job.mock.finish.assert_called_once()  # pylint: disable=no-member


@patch('khaleesi.core.models.baseModel.transaction')
@patch('khaleesi.core.batch.job.LOGGER')
@patch('khaleesi.core.batch.job.transaction')
@patch('khaleesi.core.batch.job.Paginator')
@patch('khaleesi.core.batch.job.SINGLETON')
@patch('khaleesi.core.batch.job.DbJobExecution')
class CleanupJobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job: CleanupJob

  def _setJob(self, *, request: JobExecutionRequest) -> None :
    self.job = CleanupJob(model = DbJobExecution, request = request)
    self.job.mock = MagicMock()

  # noinspection PyUnusedLocal
  def testMandatoryCleanupConfiguration(self,
      start    : MagicMock,
      singleton: MagicMock,  # pylint: disable=unused-argument
      paginator: MagicMock,
      *_       : MagicMock,
  ) -> None :
    """Test that the cleanup configuration is specified."""
    # Execute test.
    request = self._successfullyStartJob(start = start, paginator = paginator)
    with self.assertRaises(InvalidArgumentException) as context:
      self.job = CleanupJob(model = DbJobExecution, request = request)
    # Assert result.
    self.assertIn('configuration.cleanup', context.exception.publicDetails)
    self.assertIn('configuration.cleanup', context.exception.privateMessage)
    self.assertIn('configuration.cleanup', context.exception.privateDetails)

  def testJobSuccess(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_       : MagicMock,
  ) -> None :
    """Test successful job run."""
    # Prepare data.
    request = self._successfullyStartJob(start = start, paginator = paginator)
    request.jobExecution.configuration.cleanup.isCleanupJob = True
    self._setJob(request = request)
    self.job.mock.getQueryset.return_value.filter.return_value.delete.return_value = (2, 0)
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(
      GrpcJobExecution.Status.Name(GrpcJobExecution.Status.SUCCESS),
      self.job.jobExecution.status,
    )
    self.assertEqual(6          , self.job.jobExecution.totalItems)
    self.assertEqual(6          , self.job.jobExecution.itemsProcessed)
    self.assertIn('successfully', self.job.jobExecution.statusDetails)
    self.assertEqual(2          , singleton.structuredLogger.logEvent.call_count)
    self.assertEqual(1          , paginator.return_value.get_page.call_args.args[0])
