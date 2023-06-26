"""Test core-sawmill batch jobs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobRequest
from microservice.actuator.core.sawmill import (
  cleanupEvents,
  cleanupGrpcRequests,
  cleanupErrors,
  cleanupHttpRequests,
  cleanupQueries,
)


@patch('microservice.actuator.core.sawmill.STUB')
class SawmillJobTestCase(SimpleTestCase):
  """Test core-sawmill batch jobs."""

  def testCleanupEvents(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanupEvents(request)
    # Assert result.
    stub.CleanupEvents.assert_called_once_with(request)

  def testCleanupGrpcRequests(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanupGrpcRequests(request)
    # Assert result.
    stub.CleanupGrpcRequests.assert_called_once_with(request)

  def testCleanupErrors(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanupErrors(request)
    # Assert result.
    stub.CleanupErrors.assert_called_once_with(request)

  def testCleanupHttpRequests(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanupHttpRequests(request)
    # Assert result.
    stub.CleanupHttpRequests.assert_called_once_with(request)

  def testCleanupQueries(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanupQueries(request)
    # Assert result.
    stub.CleanupQueries.assert_called_once_with(request)
