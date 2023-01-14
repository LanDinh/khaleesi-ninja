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

  @patch.object(JobExecution.objects, 'filter')
  @patch.object(JobExecution.objects, 'create')
  def test_start_job_execution(self, create: MagicMock, filter_count: MagicMock) -> None :
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

  @patch.object(JobExecution.objects, 'get')
  def test_finish_job_execution(self, get: MagicMock) -> None :
    """Test finishing a job execution."""
    items_processed = 13
    details         = 'details'
    for status_label, status_type in JobExecutionResponse.Status.items():
      with self.subTest(status = status_label):
        # Prepare data.
        get.reset_mock()
        # Execute test.
        JobExecution.objects.finish_job_execution(
          job             = MagicMock(),
          status          = status_type,
          items_processed = items_processed,
          details         = details,
        )
        # Assert result.
        get.assert_called_once()
        get.return_value.save.assert_called_once_with()
        self.assertEqual(status_label   , get.return_value.status)
        self.assertEqual(items_processed, get.return_value.items_processed)
        self.assertEqual(details        , get.return_value.details)


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
          details         = 'details',
          end             = datetime.now().replace(tzinfo = timezone.utc)
        )
        # Execute test.
        result = job_execution.to_grpc_job_execution_response()
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(job_execution.job_id         , result.execution_metadata.job_id)
        self.assertEqual(job_execution.execution_id   , result.execution_metadata.execution_id)
        self.assertEqual(status_type                  , result.status)
        self.assertEqual(job_execution.items_processed, result.items_processed)
        self.assertEqual(job_execution.details        , result.details)
        self.assertEqual(job_execution.end, result.end.ToDatetime().replace(tzinfo = timezone.utc))
