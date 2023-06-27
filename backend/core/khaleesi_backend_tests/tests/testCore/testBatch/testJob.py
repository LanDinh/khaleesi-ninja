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
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobRequest


class Job(BaseJob[JobExecution]):
  """Test job for testing."""

  mock = MagicMock()

  def executeBatch(self, *, page: Page[JobExecution]) -> int :
    """Execute one batch of the job and return the number of items that were processed."""
    self.mock.executeBatch()
    return 2

  def getQueryset(self) -> QuerySet[JobExecution] :
    """Return the full queryset to be iterated over."""
    return self.mock.getQueryset()  # type: ignore[no-any-return]


class CleanupJob(BaseCleanupJob[JobExecution]):
  """Test job for testing."""

  mock = MagicMock()

  def getQueryset(self) -> QuerySet[JobExecution] :
    """Return the full queryset to be iterated over."""
    return self.mock.getQueryset()  # type: ignore[no-any-return]


class JobTestMixin:
  """Common methods for all job tests."""

  def _successfullyStartJob(self, *, start: MagicMock, paginator: MagicMock) -> JobRequest :
    """Prepare successful job start"""
    jobExecution = JobExecution()
    jobExecution.status = JobExecutionResponse.Status.Name(JobExecutionResponse.Status.IN_PROGRESS)
    jobExecution.save   = MagicMock()  # type: ignore[assignment]
    jobExecution.toGrpc = MagicMock()  # type: ignore[assignment]
    start.return_value = jobExecution
    paginator.return_value.count = 6
    paginator.return_value.page_range = [ 1, 2, 3 ]
    request = JobRequest()
    request.actionConfiguration.batchSize = 2
    request.actionConfiguration.timelimit.FromSeconds(60)
    return request


@patch('khaleesi.core.batch.job.LOGGER')
@patch('khaleesi.core.batch.job.Paginator')
@patch('khaleesi.core.batch.job.SINGLETON')
@patch('khaleesi.core.batch.job.JobExecution.objects.startJobExecution')
class JobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job: Job

  def _setJob(self, *, request: JobRequest) -> None :
    self.job = Job(model = JobExecution, request = request)
    self.job.mock = MagicMock()

  def testMandatoryBatchSize(self, *_: MagicMock) -> None :
    """Test that the batch size is specified."""
    # Execute test.
    with self.assertRaises(InvalidArgumentException) as context:
      self.job = Job(model = JobExecution, request = JobRequest())
    # Assert result.
    self.assertIn('actionConfiguration.batchSize', context.exception.publicDetails)
    self.assertIn('actionConfiguration.batchSize', context.exception.privateMessage)
    self.assertIn('actionConfiguration.batchSize', context.exception.privateDetails)

  def testMandatoryTimeLimit(self, *_: MagicMock) -> None :
    """Test that the timelimit is specified."""
    # Execute test.
    with self.assertRaises(InvalidArgumentException) as context:
      request = JobRequest()
      request.actionConfiguration.batchSize = 5
      self.job = Job(model = JobExecution, request = request)
    # Assert result.
    self.assertIn('actionConfiguration.timelimit', context.exception.publicDetails)
    self.assertIn('actionConfiguration.timelimit', context.exception.privateMessage)
    self.assertIn('actionConfiguration.timelimit', context.exception.privateDetails)

  @patch('khaleesi.core.batch.job.JobExecution')
  def testJobFailsToStart(
      self,
      jobExecution: MagicMock,
      start       : MagicMock,
      singleton   : MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test failure for the job to start."""
    # Prepare data.
    start.side_effect = Exception('start failure')
    jobExecution.return_value = JobExecution()
    jobExecution.return_value.save = MagicMock()  # type: ignore[assignment]
    request = JobRequest()
    request.actionConfiguration.batchSize = 2
    request.actionConfiguration.timelimit.FromSeconds(60)
    self._setJob(request = request)
    # Execute test.
    with self.assertRaises(Exception):
      self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ERROR),
      self.job.jobExecution.status,
    )
    self.assertEqual(0             , self.job.jobExecution.itemsProcessed)
    self.assertEqual(0             , self.job.jobExecution.totalItems)
    self.assertIn('failed to start', self.job.jobExecution.details)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    singleton.structuredLogger.logError.assert_called_once()

  def testJobIsSkipped(self, start: MagicMock, singleton: MagicMock, *_: MagicMock) -> None :
    """Test job getting skipped."""
    for statusLabel, statusType in [
        (statusLabel, statusType) for statusLabel, statusType
        in JobExecutionResponse.Status.items()
        if statusType != JobExecutionResponse.Status.IN_PROGRESS
    ]:
      with self.subTest(status = statusLabel):
        # Prepare data.
        singleton.reset_mock()
        start.reset_mock()
        start.return_value        = JobExecution()
        start.return_value.status = statusLabel
        start.return_value.toGrpc = MagicMock()  # type: ignore[assignment]
        start.return_value.save   = MagicMock()  # type: ignore[assignment]
        request = JobRequest()
        request.actionConfiguration.batchSize = 2
        request.actionConfiguration.timelimit.FromSeconds(60)
        self._setJob(request = request)
        # Execute test.
        self.job.execute(stopEvent = Event())
        # Assert result.
        self.assertEqual(
          JobExecutionResponse.Status.Name(JobExecutionResponse.Status.SKIPPED),
          self.job.jobExecution.status,
        )
        self.assertEqual(0     , self.job.jobExecution.itemsProcessed)
        self.assertEqual(0     , self.job.jobExecution.totalItems)
        self.assertIn('skipped', self.job.jobExecution.details)
        self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)

  def testJobFailedToGetCount(
      self,
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
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ERROR),
      self.job.jobExecution.status,
    )
    self.assertEqual(0                            , self.job.jobExecution.itemsProcessed)
    self.assertEqual(0                            , self.job.jobExecution.totalItems)
    self.assertIn('total amount of affected items', self.job.jobExecution.details)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    singleton.structuredLogger.logError.assert_called_once()

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
    self.assertIn('aborted', self.job.jobExecution.details)
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ABORT),
      self.job.jobExecution.status,
    )
    self.assertEqual(0, self.job.jobExecution.itemsProcessed)
    self.assertEqual(6, self.job.jobExecution.totalItems)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)

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
    request.actionConfiguration.timelimit.FromNanoseconds(1)
    self._setJob(request = request)
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertIn('timed out', self.job.jobExecution.details)
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.TIMEOUT),
      self.job.jobExecution.status,
    )
    self.assertEqual(0, self.job.jobExecution.itemsProcessed)
    self.assertEqual(6, self.job.jobExecution.totalItems)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)

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
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ERROR),
      self.job.jobExecution.status,
    )
    self.assertEqual(0       , self.job.jobExecution.itemsProcessed)
    self.assertEqual(6       , self.job.jobExecution.totalItems)
    self.assertIn('Exception', self.job.jobExecution.details)
    self.assertEqual(2, singleton.structuredLogger.logEvent.call_count)
    singleton.structuredLogger.logError.assert_called_once()
    self.job.mock.executeBatch.assert_called_once_with()

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
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.SUCCESS),
      self.job.jobExecution.status,
    )
    self.assertEqual(6          , self.job.jobExecution.totalItems)
    self.assertEqual(6          , self.job.jobExecution.itemsProcessed)
    self.assertIn('successfully', self.job.jobExecution.details)
    self.assertEqual(2          , singleton.structuredLogger.logEvent.call_count)
    self.assertEqual(3          , self.job.mock.executeBatch.call_count)
    self.assertNotEqual(1       , paginator.return_value.get_page.call_args.args[0])


@patch('khaleesi.core.batch.job.LOGGER')
@patch('khaleesi.core.batch.job.Paginator')
@patch('khaleesi.core.batch.job.SINGLETON')
@patch('khaleesi.core.batch.job.JobExecution.objects.startJobExecution')
class CleanupJobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job: CleanupJob

  def _setJob(self, *, request: JobRequest) -> None :
    self.job = CleanupJob(model = JobExecution, request = request)
    self.job.mock = MagicMock()

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
      self.job = CleanupJob(model = JobExecution, request = request)
    # Assert result.
    self.assertIn('cleanupConfiguration', context.exception.publicDetails)
    self.assertIn('cleanupConfiguration', context.exception.privateMessage)
    self.assertIn('cleanupConfiguration', context.exception.privateDetails)

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
    request.cleanupConfiguration.isCleanupJob = True
    self._setJob(request = request)
    self.job.mock.getQueryset.return_value.filter.return_value.delete.return_value = (2, 0)
    # Execute test.
    self.job.execute(stopEvent = Event())
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.SUCCESS),
      self.job.jobExecution.status,
    )
    self.assertEqual(6          , self.job.jobExecution.totalItems)
    self.assertEqual(6          , self.job.jobExecution.itemsProcessed)
    self.assertIn('successfully', self.job.jobExecution.details)
    self.assertEqual(2          , singleton.structuredLogger.logEvent.call_count)
    self.assertEqual(1          , paginator.return_value.get_page.call_args.args[0])
