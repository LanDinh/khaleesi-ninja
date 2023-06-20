"""Test basic job tracking."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.models import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse


class JobExecutionManagerTestCase(SimpleTestCase):
  """Test the job execution manager."""

  @patch('khaleesi.models.job.transaction.atomic')
  @patch.object(JobExecution.objects, 'filter')
  @patch.object(JobExecution.objects, 'create')
  def test_start_job_execution(
      self,
      create      : MagicMock,
      filter_count: MagicMock,
      *_          : MagicMock,
  ) -> None :
    """Test starting a job execution."""
    for count in [ 0, 1 ]:
      with self.subTest(count = count):
        # Prepare data.
        create.reset_mock()
        filter_count.reset_mock()
        filter_count.return_value.count.return_value = count
        # Execute test.
        JobExecution.objects.start_job_execution(job = MagicMock())
        # Assert result.
        create.assert_called_once()

  @patch('khaleesi.models.job.threading_enumerate')
  @patch.object(JobExecution.objects, 'filter')
  def test_stop_job_execution(
      self,
      filter_data        : MagicMock,
      threading_enumerate: MagicMock,
  ) -> None :
    """Test stopping a job execution."""
    # Prepare data.
    job = MagicMock()
    job.job_id = 'job-id'
    filter_data.return_value = [ job, job ]
    thread_to_stop = MagicMock()
    thread_to_stop.is_batch_job_thread = True
    thread_to_stop.is_job.side_effect  = [ True, False ]
    thread_to_not_stop = MagicMock([ 'stop' ])
    threading_enumerate.return_value = [ thread_to_stop, thread_to_not_stop ]
    # Execute test.
    JobExecution.objects.stop_job(id_message = MagicMock())
    # Assert result.
    thread_to_stop.stop.assert_called_once()
    thread_to_not_stop.stop.assert_not_called()

  @patch('khaleesi.models.job.threading_enumerate')
  def test_stop_all_jobs(self, threading_enumerate: MagicMock) -> None :
    """Test stopping a job execution."""
    # Prepare data.
    thread_to_stop = MagicMock()
    thread_to_stop.is_batch_job_thread = True
    thread_to_stop.is_job              = True
    thread_to_not_stop = MagicMock([ 'stop' ])
    threading_enumerate.return_value = [ thread_to_stop, thread_to_not_stop ]
    # Execute test.
    result = JobExecution.objects.stop_all_jobs()
    # Assert result.
    thread_to_stop.stop.assert_called_once()
    thread_to_not_stop.stop.assert_not_called()
    self.assertEqual([ thread_to_stop ], result)


class JobExecutionTestCase(SimpleTestCase):
  """Test job executions."""

  def test_in_progress(self) -> None :
    """Test if a job execution is in progress."""
    # Prepare data.
    job_execution = JobExecution(status = 'IN_PROGRESS')
    # Execute test.
    result = job_execution.in_progress
    # Assert result.
    self.assertTrue(result)

  def test_not_in_progress(self) -> None :
    """Test if a job execution is in progress."""
    for status_label, status_type in [
        (status_label, status_type)
        for status_label, status_type in JobExecutionResponse.Status.items()
        if status_type != JobExecutionResponse.Status.IN_PROGRESS
    ]:
      with self.subTest(status = status_label):
        # Prepare data.
        job_execution = JobExecution(status = status_label)
        # Execute test.
        result = job_execution.in_progress
        # Assert result.
        self.assertFalse(result)

  def test_set_total(self) -> None :
    """Test if a job execution is in progress."""
    # Prepare data.
    job_execution = JobExecution()
    job_execution.save = MagicMock()  # type: ignore[assignment]
    total = 13
    # Execute test.
    job_execution.set_total(total = 13)
    # Assert result.
    self.assertEqual(total, job_execution.total_items)
    job_execution.save.assert_called_once_with()

  def test_finish(self) -> None :
    """Test finishing a job."""
    items_processed = 13
    details         = 'details'
    for status_label, status_type in JobExecutionResponse.Status.items():
      with self.subTest(status = status_label):
        # Prepare data.
        job_execution = JobExecution()
        job_execution.save = MagicMock()  # type: ignore[assignment]
        # Execute test.
        job_execution.finish(
          status          = status_type,
          items_processed = items_processed,
          details         = details,
        )
        # Assert result.
        self.assertEqual(status_label   , job_execution.status)
        self.assertEqual(items_processed, job_execution.items_processed)
        self.assertEqual(details        , job_execution.details)
        job_execution.save.assert_called_once_with()

  @patch('khaleesi.models.job.add_request_metadata')
  def test_to_grpc_job_execution_response(self, metadata: MagicMock) -> None :
    """Test transforming a job execution into a grpc request."""
    for status_label, status_type in JobExecutionResponse.Status.items():
      with self.subTest(status = status_label):
        # Prepare data.
        metadata.reset_mock()
        job_execution = JobExecution(
          job_id          = 'job-id',
          execution_id    = 13,
          status          = status_label,
          items_processed = 42,
          total_items     = 1337,
          details         = 'details',
          end             = datetime.now().replace(tzinfo = timezone.utc)
        )
        # Execute test.
        result = job_execution.to_grpc_job_execution_response()
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(job_execution.job_id         , result.executionMetadata.jobId)
        self.assertEqual(job_execution.execution_id   , result.executionMetadata.executionId)
        self.assertEqual(status_type                  , result.status)
        self.assertEqual(job_execution.items_processed, result.itemsProcessed)
        self.assertEqual(job_execution.total_items    , result.totalItems)
        self.assertEqual(job_execution.details        , result.details)
        self.assertEqual(job_execution.end, result.end.ToDatetime().replace(tzinfo = timezone.utc))
