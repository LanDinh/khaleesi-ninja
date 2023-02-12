"""Test the core-sawmill sawyer service."""

# Python.
from typing import Callable
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobCleanupRequest
from khaleesi.proto.core_sawmill_pb2 import (
  LogFilter,
  EventResponse as GrpcEventResponse,
  RequestResponse as GrpcRequestResponse,
  ErrorResponse as GrpcErrorResponse,
  BackgateRequestResponse as GrpcBackgateResponse,
  QueryResponse as GrpcQueryResponse,
)
from microservice.models import Event, Request, Error, BackgateRequest, Query
from microservice.service.sawyer import Service

@patch('microservice.service.sawyer.LOGGER')
class SawyerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  def test_cleanup_events(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._execute_cleanup_test(method  = self.service.CleanupEvents)  # pylint: disable=no-value-for-parameter

  def test_cleanup_requests(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._execute_cleanup_test(method = self.service.CleanupRequests)  # pylint: disable=no-value-for-parameter

  def test_cleanup_errors(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._execute_cleanup_test(method = self.service.CleanupErrors)  # pylint: disable=no-value-for-parameter

  def test_cleanup_backgate_requests(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._execute_cleanup_test(method = self.service.CleanupBackgateRequests)  # pylint: disable=no-value-for-parameter

  def test_cleanup_queries(self, *_: MagicMock) -> None :
    """Test cleaning up."""
    # Execute test.
    self._execute_cleanup_test(method = self.service.CleanupQueries)  # pylint: disable=no-value-for-parameter

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

  @patch.object(Query.objects, 'filter')
  def test_get_queries(self, db_queries: MagicMock, *_: MagicMock) -> None :
    """Test getting logged requests."""
    # Prepare data.
    db_query = MagicMock()
    db_query.to_grpc_query_response.return_value = GrpcQueryResponse()
    db_queries.return_value = [ db_query ]
    # Execute test.
    result = self.service.GetQueries(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.queries))
    db_queries.assert_called_once_with()
    db_query.to_grpc_query_response.assert_called_once_with()

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

  @patch('microservice.service.sawyer.CleanupJob')
  def _execute_cleanup_test(
      self,
      cleanup: MagicMock,
      *,
      method: Callable[[JobCleanupRequest, ServicerContext], JobExecutionResponse],
  ) -> None :
    """All cleanup methods look the same, so we can have a unified test."""
    # Execute test.
    method(JobCleanupRequest(), MagicMock())
    # Assert result.
    cleanup.return_value.execute.assert_called_once()
