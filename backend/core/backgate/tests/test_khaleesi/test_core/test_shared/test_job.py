"""Test job execution."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.job import Job as BaseJob
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobCleanupRequest


class Job(BaseJob):
  """Test job for testing."""

  mock = MagicMock()

  def execute_batch(self) -> int :
    """Execute one batch of the job and return the number of items that were processed."""
    self.mock.execute_batch()
    return 1

  def count_total(self) -> int :
    """Count the total number of items that should be executed."""
    self.mock.count_total()
    return 5

  def target(self) -> str :
    """Return the target resource. By default, this is should be the affected model name."""
    self.mock.target()
    return 'target'


@patch('khaleesi.core.shared.job.LOGGER')
@patch('khaleesi.core.shared.job.SINGLETON')
@patch('khaleesi.core.shared.job.JobExecution.objects.start_job_execution')
class JobTestCase(SimpleTestCase):
  """Test job execution."""

  job = Job()

  def setUp(self) -> None :
    """Reset mocks."""
    self.job.mock.reset_mock(return_value = True, side_effect = True)
    self.job.mock.count_total.reset_mock(return_value = True, side_effect = True)
    self.job.mock.execute_batch.reset_mock(return_value = True, side_effect = True)

  def test_job_fails_to_start(self, start: MagicMock, singleton: MagicMock, _: MagicMock) -> None :
    """Test failure for the job to start."""
    # Prepare data.
    start.side_effect = Exception('start failure')
    # Execute test.
    with self.assertRaises(Exception):
      self.job.execute(request = JobCleanupRequest())
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

  def test_job_is_skipped(self, start: MagicMock, singleton: MagicMock, _: MagicMock) -> None :
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
        # Execute test.
        self.job.execute(request = JobCleanupRequest())
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
      _: MagicMock,
  ) -> None :
    """Test failure for the job to get the total count."""
    # Prepare data.
    self.job.mock.count_total.side_effect = Exception('no total count')
    self._successfully_start_job(start = start)
    # Execute test.
    self.job.execute(request = JobCleanupRequest())
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
    self.job.mock.count_total.assert_called_once_with()

  def test_job_timeout(self, start: MagicMock, singleton: MagicMock, _: MagicMock) -> None :
    """Test job timeout."""
    # Prepare data.
    self._successfully_start_job(start = start)
    # Execute test.
    self.job.execute(request = JobCleanupRequest())
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.TIMEOUT),
      self.job.job_execution.status,
    )
    self.assertEqual(0       , self.job.job_execution.items_processed)
    self.assertEqual(5       , self.job.job_execution.total_items)
    self.assertIn('timed out', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    self.job.mock.count_total.assert_called_once_with()

  def test_job_error(self, start: MagicMock, singleton: MagicMock, _: MagicMock) -> None :
    """Test job error during batch processing."""
    # Prepare data.
    self.job.mock.execute_batch.side_effect = Exception('error in batch')
    self._successfully_start_job(start = start)
    request = JobCleanupRequest()
    request.action_configuration.timelimit.FromSeconds(60)
    # Execute test.
    self.job.execute(request = request)
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ERROR),
      self.job.job_execution.status,
    )
    self.assertEqual(0       , self.job.job_execution.items_processed)
    self.assertEqual(5       , self.job.job_execution.total_items)
    self.assertIn('Exception', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    singleton.structured_logger.log_error.assert_called_once()
    self.job.mock.count_total.assert_called_once_with()
    self.job.mock.execute_batch.assert_called_once_with()

  def test_job_success(self, start: MagicMock, singleton: MagicMock, _: MagicMock) -> None :
    """Test successful job run."""
    # Prepare data.
    self._successfully_start_job(start = start)
    request = JobCleanupRequest()
    request.action_configuration.timelimit.FromSeconds(60)
    # Execute test.
    self.job.execute(request = request)
    # Assert result.
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.SUCCESS),
      self.job.job_execution.status,
    )
    self.assertEqual(5          , self.job.job_execution.items_processed)
    self.assertEqual(5          , self.job.job_execution.total_items)
    self.assertIn('successfully', self.job.job_execution.details)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)
    self.job.mock.count_total.assert_called_once_with()
    self.assertEqual(5, self.job.mock.execute_batch.call_count)

  def _successfully_start_job(self, *, start: MagicMock) -> None :
    """Prepare successful job start"""
    job_execution = JobExecution()
    job_execution.status = JobExecutionResponse.Status.Name(JobExecutionResponse.Status.IN_PROGRESS)
    job_execution.save                           = MagicMock()  # type: ignore[assignment]
    job_execution.to_grpc_job_execution_response = MagicMock()  # type: ignore[assignment]
    start.return_value                           = job_execution
