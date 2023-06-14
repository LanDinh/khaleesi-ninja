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
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobRequest


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

  def _successfully_start_job(self, *, start: MagicMock, paginator: MagicMock) -> JobRequest :
    """Prepare successful job start"""
    job_execution = JobExecution()
    job_execution.status = JobExecutionResponse.Status.Name(JobExecutionResponse.Status.IN_PROGRESS)
    job_execution.save                           = MagicMock()  # type: ignore[assignment]
    job_execution.to_grpc_job_execution_response = MagicMock()  # type: ignore[assignment]
    start.return_value                           = job_execution
    paginator.return_value.count = 6
    paginator.return_value.page_range = [ 1, 2, 3 ]
    request = JobRequest()
    request.action_configuration.batch_size = 2
    request.action_configuration.timelimit.FromSeconds(60)
    return request


@patch('khaleesi.core.batch.job.LOGGER')
@patch('khaleesi.core.batch.job.Paginator')
@patch('khaleesi.core.batch.job.SINGLETON')
@patch('khaleesi.core.batch.job.JobExecution.objects.start_job_execution')
class JobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job: Job

  def _set_job(self, *, request: JobRequest) -> None :
    self.job = Job(model = JobExecution, request = request)
    self.job.mock = MagicMock()

  def test_mandatory_batch_size(self, *_: MagicMock) -> None :
    """Test that the batch size is specified."""
    # Execute test.
    with self.assertRaises(InvalidArgumentException) as context:
      self.job = Job(model = JobExecution, request = JobRequest())
    # Assert result.
    self.assertIn('action_configuration.batch_size', context.exception.public_details)
    self.assertIn('action_configuration.batch_size', context.exception.private_message)
    self.assertIn('action_configuration.batch_size', context.exception.private_details)

  def test_mandatory_time_limit(self, *_: MagicMock) -> None :
    """Test that the timelimit is specified."""
    # Execute test.
    with self.assertRaises(InvalidArgumentException) as context:
      request = JobRequest()
      request.action_configuration.batch_size = 5
      self.job = Job(model = JobExecution, request = request)
    # Assert result.
    self.assertIn('action_configuration.timelimit', context.exception.public_details)
    self.assertIn('action_configuration.timelimit', context.exception.private_message)
    self.assertIn('action_configuration.timelimit', context.exception.private_details)

  @patch('khaleesi.core.batch.job.JobExecution')
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
    request = JobRequest()
    request.action_configuration.batch_size = 2
    request.action_configuration.timelimit.FromSeconds(60)
    self._set_job(request = request)
    # Execute test.
    with self.assertRaises(Exception):
      self.job.execute(stop_event = Event())
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
        singleton.reset_mock()
        start.reset_mock()
        start.return_value                                = JobExecution()
        start.return_value.status                         = status_label
        start.return_value.to_grpc_job_execution_response = MagicMock()  # type: ignore[assignment]
        start.return_value.save                           = MagicMock()  # type: ignore[assignment]
        request = JobRequest()
        request.action_configuration.batch_size = 2
        request.action_configuration.timelimit.FromSeconds(60)
        self._set_job(request = request)
        # Execute test.
        self.job.execute(stop_event = Event())
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
    self._set_job(request = request)
    # Execute test.
    self.job.execute(stop_event = Event())
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

  def test_job_abort(
      self,
      start    : MagicMock,
      singleton: MagicMock,
      paginator: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test job timeout."""
    # Prepare data.
    request = self._successfully_start_job(start = start, paginator = paginator)
    self._set_job(request = request)
    stop_event = Event()
    stop_event.set()
    # Execute test.
    self.job.execute(stop_event = stop_event)
    # Assert result.
    self.assertIn('aborted', self.job.job_execution.details)
    self.assertEqual(
      JobExecutionResponse.Status.Name(JobExecutionResponse.Status.ABORT),
      self.job.job_execution.status,
    )
    self.assertEqual(0       , self.job.job_execution.items_processed)
    self.assertEqual(6       , self.job.job_execution.total_items)
    self.assertEqual(2, singleton.structured_logger.log_event.call_count)

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
    request.action_configuration.timelimit.FromNanoseconds(1)
    self._set_job(request = request)
    # Execute test.
    self.job.execute(stop_event = Event())
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
    request = self._successfully_start_job(start = start, paginator = paginator)
    self._set_job(request = request)
    self.job.mock.execute_batch.side_effect = Exception('error in batch')
    # Execute test.
    self.job.execute(stop_event = Event())
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
    self._set_job(request = request)
    # Execute test.
    self.job.execute(stop_event = Event())
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


@patch('khaleesi.core.batch.job.LOGGER')
@patch('khaleesi.core.batch.job.Paginator')
@patch('khaleesi.core.batch.job.SINGLETON')
@patch('khaleesi.core.batch.job.JobExecution.objects.start_job_execution')
class CleanupJobTestCase(SimpleTestCase, JobTestMixin):
  """Test job execution."""

  job: CleanupJob

  def _set_job(self, *, request: JobRequest) -> None :
    self.job = CleanupJob(model = JobExecution, request = request)
    self.job.mock = MagicMock()

  def test_job_success(
      self,
      start        : MagicMock,
      singleton    : MagicMock,
      paginator    : MagicMock,
      *_           : MagicMock,
  ) -> None :
    """Test successful job run."""
    # Prepare data.
    request = self._successfully_start_job(start = start, paginator = paginator)
    self._set_job(request = request)
    self.job.mock.get_queryset.return_value.filter.return_value.delete.return_value = (2, 0)
    # Execute test.
    self.job.execute(stop_event = Event())
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
