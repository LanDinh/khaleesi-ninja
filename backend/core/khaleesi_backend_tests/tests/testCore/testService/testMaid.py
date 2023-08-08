"""Test the core maid service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.core.service.maid import Service
from khaleesi.models.jobExecution import JobExecution
from khaleesi.proto.core_pb2 import ObjectMetadataRequest, EmptyRequest


@patch('khaleesi.core.service.maid.LOGGER')
class MaidServiceTestCase(SimpleTestCase):
  """Test the core maid service."""

  service = Service()

  @patch.object(JobExecution.objects, 'getJobExecutionsInProgress')
  @patch('khaleesi.core.service.maid.stopJob')
  def testAbortBatchJob(self, stopJob: MagicMock, jobExecutions: MagicMock, *_: MagicMock) -> None :
    """Test aborting a specific job."""
    # Execute test.
    self.service.AbortBatchJob(ObjectMetadataRequest(), MagicMock())
    # Assert result.
    stopJob.assert_called_once()
    jobExecutions.assert_called_once()

  @patch('khaleesi.core.service.maid.stopAllJobs')
  def testAbortAllBatchJobs(self, stopAllJobs: MagicMock, *_: MagicMock) -> None :
    """Test aborting a specific job."""
    # Execute test.
    self.service.AbortAllBatchJobs(EmptyRequest(), MagicMock())
    # Assert result.
    stopAllJobs.assert_called_once()
