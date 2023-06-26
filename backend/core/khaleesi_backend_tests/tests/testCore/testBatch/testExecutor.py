"""Test the executor for jobs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.batch.executor import jobExecutor
from khaleesi.core.testUtil.testCase import SimpleTestCase


class JobExecutorTestCase(SimpleTestCase):
  """Test the executor for jobs."""

  @patch('khaleesi.core.batch.executor.BatchJobThread')
  def testJobExecutor(self, thread: MagicMock) -> None :
    """Test executing the job."""
    # Execute test.
    jobExecutor(job = MagicMock())
    # Assert result.
    thread.return_value.start.assert_called_once_with()
