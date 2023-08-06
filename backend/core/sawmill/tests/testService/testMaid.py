"""Test the core-sawmill maid service."""

# Python.
from typing import Callable
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionRequest, EmptyResponse
from microservice.service.maid import Service

@patch('microservice.service.maid.LOGGER')
class MaidServiceTestCase(SimpleTestCase):
  """Test the core-sawmill maid service."""

  service = Service()

  def testCleanupHttpRequests(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._executeCleanupTest(method = self.service.CleanupHttpRequests)  # pylint: disable=no-value-for-parameter

  def testCleanupGrpcRequests(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._executeCleanupTest(method = self.service.CleanupGrpcRequests)  # pylint: disable=no-value-for-parameter

  def testCleanupEvents(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._executeCleanupTest(method  = self.service.CleanupEvents)  # pylint: disable=no-value-for-parameter

  def testCleanupErrors(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._executeCleanupTest(method = self.service.CleanupErrors)  # pylint: disable=no-value-for-parameter

  def testCleanupQueries(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._executeCleanupTest(method = self.service.CleanupQueries)  # pylint: disable=no-value-for-parameter

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
