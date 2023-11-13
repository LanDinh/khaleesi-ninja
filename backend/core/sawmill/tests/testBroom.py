"""Test the core-sawmill maid service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionRequest
from microservice.broom import Broom


class MaidServiceTestCase(SimpleTestCase):
  """Test the core-sawmill maid service."""

  broom = Broom()

  @patch('microservice.broom.CleanupJob')
  @patch('microservice.broom.jobExecutor')
  def testCleanup(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    for action in [ 'events', 'grpc-requests', 'errors', 'http-requests', 'queries' ]:
      with self.subTest(action = action):
        # Prepare data.
        jobExecutionRequest = JobExecutionRequest()
        jobExecutionRequest.jobExecution.action.action = f'cleanup-${action}'
        # Execute test & assert result.
        self.broom.cleanup(jobExecutionRequest = jobExecutionRequest)


  def testCleanupFailure(self) -> None :
    """Test not cleaning up."""
    # Prepare data.
    jobExecutionRequest = JobExecutionRequest()
    jobExecutionRequest.jobExecution.action.action = 'not-existing-action'
    # Execute test & assert result.
    with self.assertRaises(ProgrammingException):
      self.broom.cleanup(jobExecutionRequest = jobExecutionRequest)
