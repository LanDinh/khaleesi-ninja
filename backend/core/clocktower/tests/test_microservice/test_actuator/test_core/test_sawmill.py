"""Test core-sawmill batch jobs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import JobCleanupRequest
from microservice.actuator.core.sawmill import cleanup_requests


@patch('microservice.actuator.core.sawmill.STUB')
class SawmillJobTestCase(SimpleTestCase):
  """Test core-sawmill batch jobs."""

  def test_cleanup_requests(self, stub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobCleanupRequest()
    # Execute test.
    cleanup_requests(request)
    # Assert result.
    stub.CleanupRequests.assert_called_once_with(request)
