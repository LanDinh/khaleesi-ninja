"""Test job execution."""

# Python.
from unittest.mock import patch, MagicMock, PropertyMock

# Django.
from django.core.paginator import Page
from django.db.models import QuerySet

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.shared.job import Job as BaseJob, CleanupJob as BaseCleanupJob
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobCleanupRequest


class Job(BaseJob[JobExecution]):
  """Test job for testing."""

  mock = MagicMock()

  def execute_batch(self, *, page: Page[JobExecution]) -> int :
    """Execute one batch of the job and return the number of items that were processed."""
    self.mock.execute_batch()
    return 2

  def get_queryset(self) -> QuerySet[JobExecution] :
    """Return the full queryset to be iterated over."""
    return self.mock.get_queryset()  # type: ignore[no-any-return]


class CleanupJob(BaseCleanupJob[JobExecution]):
  """Test job for testing."""

  mock = MagicMock()

  def get_queryset(self) -> QuerySet[JobExecution] :
    """Return the full queryset to be iterated over."""
    return self.mock.get_queryset()  # type: ignore[no-any-return]


class JobTestMixin:
  """Common methods for all job tests."""

  def _successfully_start_job(
      self, *,
      start    : MagicMock,
      paginator: MagicMock,
  ) -> JobCleanupRequest :
    """Prepare successful job start"""
    job_execution = JobExecution()
    job_execution.status = JobExecutionResponse.Status.Name(JobExecutionResponse.Status.IN_PROGRESS)
    job_execution.save                           = MagicMock()  # type: ignore[assignment]
    job_execution.to_grpc_job_execution_response = MagicMock()  # type: ignore[assignment]
    start.return_value                           = job_execution
    paginator.return_value.count = 6
    paginator.return_value.page_range = [ 1, 2, 3 ]
    request = JobCleanupRequest()
    request.action_configuration.batch_size = 2
    return request


@patch('khaleesi.core.shared.job.LOGGER')
@patch('khaleesi.core.shared.job.Paginator')
@patch('khaleesi.core.shared.job.SINGLETON')
@patch('khaleesi.core.shared.job.JobExecution.objects.start_job_execution')
class JobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job = Job(model = JobExecution)

  def setUp(self) -> None :
    """Reset mocks."""
    self.job.mock = MagicMock()

  def test_mandatory_batch_size(self, *_: MagicMock) -> None :
    """Test that the batch size is specified."""
    # Execute test.
    with self.assertRaises(InvalidArgumentException) as context:
      self.job.execute(request = JobCleanupRequest())
    # Assert result.
    self.assertIn('action_configuration.batch_size', context.exception.public_details)
    self.assertIn('action_configuration.batch_size', context.exception.private_message)
    self.assertIn('action_configuration.batch_size', context.exception.private_details)

  @patch('khaleesi.core.shared.job.JobExecution')
  def test_job_fails_to_start(
      self,
      job_execution: MagicMock,
      start        : MagicMock,
      singleton    : MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test failure for the job to start."""
    # Prepare data.
    start.side_effect = Exception('start failure')
    job_execution.return_value = JobExecution()
    job_execution.return_value.save = MagicMock()  # type: ignore[assignment]
    request = JobCleanupRequest()
    request.action_configuration.batch_size = 2
    # Execute test.
    with self.assertRaises(Exception):
      self.job.execute(request = request)
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ERROR),
      self.job.job_execution.status,
    )
    self.assertEqual(0             , self.job.job_execution.items_processed)
    self.assertEqual(0             , self.job.job_execution.total_items)
    self.assertIn('failed to start', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    singleton.structured_logger.log_error.assert_called_once()

  def test_job_is_skipped(self, start: MagicMock, singleton: MagicMock, *_: MagicMock) -> None :
    """Test job getting skipped."""
    for status_label, status_type in [
        (status_label, status_type) for status_label, status_type
        in JobExecutionResponse.Status.items()
        if status_type != JobExecutionResponse.Status.IN_PROGRESS
    ]:
      with self.subTest(status = status_label):
        # Prepare data.
        self.setUp()
        singleton.reset_mock()
        start.reset_mock()
        start.return_value                                = JobExecution()
        start.return_value.status                         = status_label
        start.return_value.to_grpc_job_execution_response = MagicMock()  # type: ignore[assignment]
        start.return_value.save                           = MagicMock()  # type: ignore[assignment]
        request = JobCleanupRequest()
        request.action_configuration.batch_size = 2
        # Execute test.
        self.job.execute(request = request)
        # Assert result.
        self.assertEqual(
          JobExecutionResponse.Status.Name(JobExecutionResponse.Status.SKIPPED),
          self.job.job_execution.status,
        )
        self.assertEqual(0     , self.job.job_execution.items_processed)
        self.assertEqual(0     , self.job.job_execution.total_items)
        self.assertIn('skipped', self.job.job_execution.details)
        self.assertEqual(2, singleton.structured_logger.log_event.call_count)

  def test_job_failed_to_get_count(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test failure for the job to get the total count."""
    # Prepare data.
    request = self._successfully_start_job(start = start, paginator = paginator)
    type(paginator.return_value).count = PropertyMock(side_effect = Exception('no total count'))
    # Execute test.
    self.job.execute(request = request)
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ERROR),
      self.job.job_execution.status,
    )
    self.assertEqual(0                            , self.job.job_execution.items_processed)
    self.assertEqual(0                            , self.job.job_execution.total_items)
    self.assertIn('total amount of affected items', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    singleton.structured_logger.log_error.assert_called_once()

  def test_job_timeout(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test job timeout."""
    # Prepare data.
    request = self._successfully_start_job(start = start, paginator = paginator)
    # Execute test.
    self.job.execute(request = request)
    # Assert result.
    self.assertIn('timed out', self.job.job_execution.details)
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.TIMEOUT),
      self.job.job_execution.status,
    )
    self.assertEqual(0       , self.job.job_execution.items_processed)
    self.assertEqual(6       , self.job.job_execution.total_items)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)

  def test_job_error(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test job error during batch processing."""
    # Prepare data.
    self.job.mock.execute_batch.side_effect = Exception('error in batch')
    request = self._successfully_start_job(start = start, paginator = paginator)
    request.action_configuration.timelimit.FromSeconds(60)
    # Execute test.
    self.job.execute(request = request)
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ERROR),
      self.job.job_execution.status,
    )
    self.assertEqual(0       , self.job.job_execution.items_processed)
    self.assertEqual(6       , self.job.job_execution.total_items)
    self.assertIn('Exception', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    singleton.structured_logger.log_error.assert_called_once()
    self.job.mock.execute_batch.assert_called_once_with()

  def test_job_success(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test successful job run."""
    # Prepare data.
    request = self._successfully_start_job(start = start, paginator = paginator)
    request.action_configuration.timelimit.FromSeconds(60)
    # Execute test.
    self.job.execute(request = request)
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.SUCCESS),
      self.job.job_execution.status,
    )
    self.assertEqual(6          , self.job.job_execution.total_items)
    self.assertEqual(6          , self.job.job_execution.items_processed)
    self.assertIn('successfully', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    self.assertEqual(3, self.job.mock.execute_batch.call_count)
    self.assertNotEqual(1, paginator.return_value.get_page.call_args.args[0])


@patch('khaleesi.core.shared.job.LOGGER')
@patch('tests.test_khaleesi.test_core.test_shared.test_job.JobExecution.objects.filter')
@patch('khaleesi.core.shared.job.Paginator')
@patch('khaleesi.core.shared.job.SINGLETON')
@patch('khaleesi.core.shared.job.JobExecution.objects.start_job_execution')
class CleanupJobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job = CleanupJob(model = JobExecution)

  def test_job_success(
      self,
      start        : MagicMock,
      singleton    : MagicMock,
      paginator    : MagicMock,
      filter_delete: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test successful job run."""
    # Prepare data.
    request = self._successfully_start_job(start = start, paginator = paginator)
    request.action_configuration.timelimit.FromSeconds(60)
    filter_delete.return_value.delete.return_value = (2, 0)
    # Execute test.
    self.job.execute(request = request)
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.SUCCESS),
      self.job.job_execution.status,
    )
    self.assertEqual(6          , self.job.job_execution.total_items)
    self.assertEqual(6          , self.job.job_execution.items_processed)
    self.assertIn('successfully', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    self.assertEqual(1, paginator.return_value.get_page.call_args.args[0])
