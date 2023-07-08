"""Test the request cleanup."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionRequest
from microservice.models.cleanupJob import CleanupJob
from tests.models import Metadata


class TestCleanupJob(SimpleTestCase):
  """Test the request cleanup."""

  @patch('tests.models.Metadata.objects.filter')
  def testGetQueryset(self, filterRequests: MagicMock) -> None :
    """Test executing a batch."""
    # Prepare data.
    request = JobExecutionRequest()
    request.jobExecution.actionConfiguration.batchSize = 1
    request.jobExecution.actionConfiguration.timelimit.FromSeconds(60)
    request.jobExecution.cleanupConfiguration.isCleanupJob = True
    job: CleanupJob[Metadata] = CleanupJob(model = Metadata, request = request)
    filterRequests.reset_mock()  # Is getting called in the __init__ method.
    # Execute test.
    job.getQueryset()
    # Assert result.
    filterRequests.assert_called_once()
