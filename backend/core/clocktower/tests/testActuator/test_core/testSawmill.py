"""Test core-sawmill batch jobs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionRequest
from microservice.actuator.core.sawmill import cleanup


@patch('microservice.actuator.core.sawmill.CLEANUP_STUB')
class SawmillJobTestCase(SimpleTestCase):
  """Test core-sawmill batch jobs."""

  def testCleanup(self, cleanupStub: MagicMock) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    request = JobExecutionRequest()
    # Execute test.
    cleanup(request)
    # Assert result.
    cleanupStub.Cleanup.assert_called_once_with(request)
