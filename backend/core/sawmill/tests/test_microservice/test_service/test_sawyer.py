"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import (
  LogFilter,
  EventResponse as GrpcEventResponse,
  RequestResponse as GrpcRequestResponse,
)
from microservice.models import Event, Request
from microservice.service.sawyer import Service

class SawyerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch.object(Event.objects, 'filter')
  def test_get_events(self, db_events: MagicMock) -> None :
    """Test getting logged events."""
    # Prepare data.
    db_event = MagicMock()
    db_event.to_grpc_event_response.return_value = GrpcEventResponse()
    db_events.return_value = [ db_event ]
    # Execute test.
    result = self.service.GetEvents(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.events))
    db_events.assert_called_once_with()
    db_event.to_grpc_event_response.assert_called_once_with()

  @patch.object(Request.objects, 'filter')
  def test_get_requests(self, db_requests: MagicMock) -> None :
    """Test getting logged requests."""
    # Prepare data.
    db_request = MagicMock()
    db_request.to_grpc_request_response.return_value = GrpcRequestResponse()
    db_requests.return_value = [ db_request]
    # Execute test.
    result = self.service.GetRequests(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.requests))
    db_requests.assert_called_once_with()
    db_request.to_grpc_request_response.assert_called_once_with()
