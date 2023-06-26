"""Test the core-sawmill forester service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import EmptyRequest
from microservice.service.forester import Service

@patch('microservice.service.forester.LOGGER')
class ForesterServiceTestCase(SimpleTestCase):
  """Test the core-sawmill forester service."""

  service = Service()

  @patch('microservice.service.forester.SERVICE_REGISTRY')
  def testGetServiceCallData(self, serviceRegistry: MagicMock, *_: MagicMock) -> None :
    """Test getting service call data."""
    # Execute test.
    self.service.GetServiceCallData(EmptyRequest(), MagicMock())
    # Assert result.
    serviceRegistry.getCallData.assert_called_once()
