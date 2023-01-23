"""Test job execution."""

# Python.
from functools import partial
from unittest.mock import patch, MagicMock
from typing import Tuple, Any

# khaleesi.ninja.
from khaleesi.core.shared.job import job
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobCleanupRequest


@patch('khaleesi.core.shared.job.LOGGER')
class JobTestCase(SimpleTestCase):
  """Test job execution."""

  @patch('khaleesi.core.shared.job.JobExecution.objects.start_job_execution')
  def test_job_ok(self, start: MagicMock, *_: MagicMock) -> None :
    """Test job execution."""
    items_processed = 13
    details         = 'details'
    cleanup_request = JobCleanupRequest()
    method          = MagicMock()
    for status_label, status_type in JobExecutionResponse.Status.items():
      with self.subTest(status = status_label):
        # Prepare data.
        start.reset_mock()
        start.return_value = MagicMock(in_progress = True)
        method.reset_mock()
        def batch(
            obj    : Any,  # pylint: disable=unused-argument
            request: JobCleanupRequest,
            *,
            status: 'JobExecutionResponse.Status.V',
        ) -> Tuple['JobExecutionResponse.Status.V', int, str] :
          """Test batching."""
          method()
          return status, items_processed, details
        # Execute test.
        job()(partial(batch, status = status_type))(MagicMock(), cleanup_request)
        # Assert result.
        method.assert_called_once_with()
        start.assert_called_once()
        start.return_value.finish.assert_called_once_with(
          status          = status_type,
          items_processed = items_processed,
          details         = details,
        )

  @patch('khaleesi.core.shared.job.JobExecution.objects.start_job_execution')
  def test_job_not_ok(self, start: MagicMock, *_: MagicMock) -> None :
    """Test job execution."""
    cleanup_request = JobCleanupRequest()
    method          = MagicMock()
    for status_label, status_type in JobExecutionResponse.Status.items():  # pylint: disable=unused-variable
      with self.subTest(status = status_label):
        # Prepare data.
        start.reset_mock()
        start.return_value = MagicMock(in_progress = True)
        method.reset_mock()
        @job()
        def batch(
            obj: Any,  # pylint: disable=unused-argument
            request: JobCleanupRequest,
        ) -> Tuple['JobExecutionResponse.Status.V', int, str] :
          """Test batching."""
          method()
          raise Exception('exception')
        # Execute test.
        batch(MagicMock(), cleanup_request)
        # Assert result.
        method.assert_called_once_with()
        start.assert_called_once()
        start.return_value.finish.assert_called_once_with(
          status          = JobExecutionResponse.Status.ERROR,
          items_processed = -1,
          details         = 'Exception happened during job execution.',
        )

  @patch('khaleesi.core.shared.job.JobExecution.objects.start_job_execution')
  def test_job_skip(self, start: MagicMock, *_: MagicMock) -> None :
    """Test job execution."""
    items_processed = 13
    details         = 'details'
    cleanup_request = JobCleanupRequest()
    method          = MagicMock()
    for status_label, status_type in JobExecutionResponse.Status.items():
      with self.subTest(status = status_label):
        # Prepare data.
        start.reset_mock()
        start.return_value = MagicMock(in_progress = False)
        method.reset_mock()
        def batch(
            obj    : Any,  # pylint: disable=unused-argument
            request: JobCleanupRequest,
            *,
            status: 'JobExecutionResponse.Status.V',
        ) -> Tuple['JobExecutionResponse.Status.V', int, str] :
          """Test batching."""
          method()
          return status, items_processed, details
        # Execute test.
        job()(partial(batch, status = status_type))(MagicMock(), cleanup_request)
        # Assert result.
        method.assert_not_called()
        start.assert_called_once()
        start.return_value.finish.assert_not_called()
