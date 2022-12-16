"""Test the core-sawmill forester service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import EmptyRequest
from microservice.service.forester import Service

@patch('microservice.service.forester.LOGGER')
class ForesterServiceTestCase(SimpleTestCase):
  """Test the core-sawmill forester service."""

  service = Service()

  @patch('microservice.service.forester.SERVICE_REGISTRY')
  def test_get_service_call_data(self, service_registry: MagicMock) -> None :
    """Test getting service call data."""
    # Execute test.
    self.service.GetServiceCallData(EmptyRequest(), MagicMock())
    # Assert result.
    service_registry.get_call_data.assert_called_once()
