"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import (
  LogFilter,
  EventResponse as GrpcEventResponse,
  RequestResponse as GrpcRequestResponse,
  ErrorResponse as GrpcErrorResponse,
  BackgateRequestResponse as GrpcBackgateResponse,
)
from microservice.models import Event, Request, Error, BackgateRequest
from microservice.service.sawyer import Service

@patch('microservice.service.sawyer.LOGGER')
class SawyerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch.object(Event.objects, 'filter')
  def test_get_events(self, db_events: MagicMock, *_: MagicMock) -> None :
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

  @patch.object(BackgateRequest.objects, 'filter')
  def test_get_backgate_requests(self, db_requests: MagicMock, *_: MagicMock) -> None :
    """Test getting logged backgate requests."""
    # Prepare data.
    db_request = MagicMock()
    db_request.to_grpc_backgate_request_response.return_value = GrpcBackgateResponse()
    db_requests.return_value = [ db_request ]
    # Execute test.
    result = self.service.GetBackgateRequests(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.requests))
    db_requests.assert_called_once_with()
    db_request.to_grpc_backgate_request_response.assert_called_once_with()

  @patch.object(Request.objects, 'filter')
  def test_get_requests(self, db_requests: MagicMock, *_: MagicMock) -> None :
    """Test getting logged requests."""
    # Prepare data.
    db_request = MagicMock()
    db_request.to_grpc_request_response.return_value = GrpcRequestResponse()
    db_requests.return_value = [ db_request ]
    # Execute test.
    result = self.service.GetRequests(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.requests))
    db_requests.assert_called_once_with()
    db_request.to_grpc_request_response.assert_called_once_with()

  @patch.object(Error.objects, 'filter')
  def test_get_errors(self, db_errors: MagicMock, *_: MagicMock) -> None :
    """Test getting logged events."""
    # Prepare data.
    db_error = MagicMock()
    db_error.to_grpc_error_response.return_value = GrpcErrorResponse()
    db_errors.return_value = [ db_error ]
    # Execute test.
    result = self.service.GetErrors(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.errors))
    db_errors.assert_called_once_with()
    db_error.to_grpc_error_response.assert_called_once_with()
