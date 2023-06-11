"""Test core-sawmill batch jobs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import JobRequest
from microservice.actuator.core.sawmill import (
  cleanup_events,
  cleanup_requests,
  cleanup_errors,
  cleanup_backgate_requests,
  cleanup_queries,
)


@patch('microservice.actuator.core.sawmill.STUB')
class SawmillJobTestCase(SimpleTestCase):
  """Test core-sawmill batch jobs."""

  def test_cleanup_events(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanup_events(request)
    # Assert result.
    stub.CleanupEvents.assert_called_once_with(request)

  def test_cleanup_requests(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanup_requests(request)
    # Assert result.
    stub.CleanupRequests.assert_called_once_with(request)

  def test_cleanup_errors(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanup_errors(request)
    # Assert result.
    stub.CleanupErrors.assert_called_once_with(request)

  def test_cleanup_backgate_requests(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanup_backgate_requests(request)
    # Assert result.
    stub.CleanupBackgateRequests.assert_called_once_with(request)

  def test_cleanup_queries(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobRequest()
    # Execute test.
    cleanup_queries(request)
    # Assert result.
    stub.CleanupQueries.assert_called_once_with(request)
