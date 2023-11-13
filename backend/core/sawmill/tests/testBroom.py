"""Test the core-sawmill maid service."""

# Python.
from typing import Callable
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionRequest, EmptyResponse
from microservice.broom import Broom

@patch('microservice.service.maid.LOGGER')
class MaidServiceTestCase(SimpleTestCase):
  """Test the core-sawmill maid service."""

  broom = Broom()

  @patch('microservice.service.maid.CleanupJob')
  @patch('microservice.service.maid.jobExecutor')
  def testCleanup(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    for action in [ 'events', 'grpc-requests', 'errors', 'http-requests', 'queries' ]:
      with self.subTest(action = action):
        # Prepare data.
        jobExecutionRequest = JobExecutionRequest()
        jobExecutionRequest.jobExecution.action.action = f'cleanup-${action}'
        # Execute test & assert result.
        self.broom.cleanup(jobExecutionRequest = jobExecutionRequest)


  def testCleanupFailure(self, *_: MagicMock) -> None :
    """Test not cleaning up."""
    # Prepare data.
    jobExecutionRequest = JobExecutionRequest()
    jobExecutionRequest.jobExecution.action.action = 'not-existing-action'
    # Execute test & assert result.
    with self.assertRaises(ProgrammingException):
      self.broom.cleanup(jobExecutionRequest = jobExecutionRequest)

  @patch('microservice.service.maid.CleanupJob')
  @patch('microservice.service.maid.jobExecutor')
  def _executeCleanupTest(
      self,
      executor: MagicMock,
      cleanup : MagicMock,
      *,
      method: Callable[[JobExecutionRequest, ServicerContext], EmptyResponse],
  ) -> None :
    """All cleanup methods look the same, so we can have a unified test."""
    # Execute test.
    method(JobExecutionRequest(), MagicMock())
    # Assert result.
    executor.assert_called_once_with(job = cleanup.return_value)
