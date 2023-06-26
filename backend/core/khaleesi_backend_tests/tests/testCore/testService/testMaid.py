"""Test the core maid service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.core.service.maid import Service
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import IdRequest, EmptyRequest


@patch('khaleesi.core.service.maid.LOGGER')
class MaidServiceTestCase(SimpleTestCase):
  """Test the core maid service."""

  service = Service()

  @patch.object(JobExecution.objects, 'stopJob')
  def testAbortBatchJob(self, stopJob: MagicMock, *_: MagicMock) -> None :
    """Test aborting a specific job."""
    # Execute test.
    self.service.AbortBatchJob(IdRequest(), MagicMock())
    # Assert result.
    stopJob.assert_called_once()

  @patch.object(JobExecution.objects, 'stopAllJobs')
  def testAbortAllBatchJobs(self, stopJob: MagicMock, *_: MagicMock) -> None :
    """Test aborting a specific job."""
    # Execute test.
    self.service.AbortAllBatchJobs(EmptyRequest(), MagicMock())
    # Assert result.
    stopJob.assert_called_once()
