"""Test the executor for jobs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.batch.executor import job_executor
from khaleesi.core.test_util.test_case import SimpleTestCase


class JobExecutorTestCase(SimpleTestCase):
  """Test the executor for jobs."""

  @patch('khaleesi.core.batch.executor.BatchJobThread')
  def test_job_executor(self, thread: MagicMock) -> None :
    """Test executing the job."""
    # Execute test.
    job_executor(job = MagicMock())
    # Assert result.
    thread.return_value.start.assert_called_once_with()
