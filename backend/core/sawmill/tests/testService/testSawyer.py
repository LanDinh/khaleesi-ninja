"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import (
  LogFilter,
  EventRequest as GrpcEventRequest,
  GrpcRequestResponse as GrpcGrpcRequestResponse,
  ErrorResponse as GrpcErrorResponse,
  HttpRequestResponse as GrpcHttpResponse,
  QueryResponse as GrpcQueryResponse,
)
from microservice.models import Event as DbEvent, GrpcRequest, Error, HttpRequest, Query
from microservice.service.sawyer import Service

@patch('microservice.service.sawyer.LOGGER')
class SawyerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch.object(DbEvent.objects, 'filter')
  def testGetEvents(self, dbEvents: MagicMock, *_: MagicMock) -> None :
    """Test getting logged events."""
    # Prepare data.
    dbEvent = MagicMock()
    dbEvent.toGrpc.return_value = GrpcEventRequest()
    dbEvents.return_value       = [ dbEvent]
    # Execute test.
    result = self.service.GetEvents(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.events))
    dbEvents.assert_called_once_with()
    dbEvent.toGrpc.assert_called_once_with()

  @patch.object(HttpRequest.objects, 'filter')
  def testGetHttpRequests(self, dbRequests: MagicMock, *_: MagicMock) -> None :
    """Test getting logged HTTP requests."""
    # Prepare data.
    dbRequest = MagicMock()
    dbRequest.toGrpc.return_value = GrpcHttpResponse()
    dbRequests.return_value       = [ dbRequest ]
    # Execute test.
    result = self.service.GetHttpRequests(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.requests))
    dbRequests.assert_called_once_with()
    dbRequest.toGrpc.assert_called_once_with()

  @patch.object(GrpcRequest.objects, 'filter')
  def testGetRequests(self, dbRequests: MagicMock, *_: MagicMock) -> None :
    """Test getting logged requests."""
    # Prepare data.
    dbRequest = MagicMock()
    dbRequest.toGrpc.return_value = GrpcGrpcRequestResponse()
    dbRequests.return_value       = [ dbRequest ]
    # Execute test.
    result = self.service.GetGrpcRequests(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.requests))
    dbRequests.assert_called_once_with()
    dbRequest.toGrpc.assert_called_once_with()

  @patch.object(Query.objects, 'filter')
  def testGetQueries(self, dbQueries: MagicMock, *_: MagicMock) -> None :
    """Test getting logged requests."""
    # Prepare data.
    dbQuery = MagicMock()
    dbQuery.toGrpc.return_value = GrpcQueryResponse()
    dbQueries.return_value      = [ dbQuery ]
    # Execute test.
    result = self.service.GetQueries(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.queries))
    dbQueries.assert_called_once_with()
    dbQuery.toGrpc.assert_called_once_with()

  @patch.object(Error.objects, 'filter')
  def testGetErrors(self, dbErrors: MagicMock, *_: MagicMock) -> None :
    """Test getting logged events."""
    # Prepare data.
    dbError = MagicMock()
    dbError.toGrpc.return_value = GrpcErrorResponse()
    dbErrors.return_value       = [ dbError ]
    # Execute test.
    result = self.service.GetErrors(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.errors))
    dbErrors.assert_called_once_with()
    dbError.toGrpc.assert_called_once_with()
