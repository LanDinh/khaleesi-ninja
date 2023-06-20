"""Test the core-sawmill lumberjack service."""

# Python.
from datetime import datetime, timezone, timedelta
from typing import Callable, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.service.lumberjack import (  # type: ignore[attr-defined]
  Service,
  DbEvent,
  DbGrpcRequest,
  DbError,
  DbHttpRequest,
  DbQuery,
)
from tests.models import Metadata


@patch('microservice.service.lumberjack.LOGGER')
class LumberjackServiceTestCase(SimpleTestCase):
  """Test the core-sawmill lumberjack service."""

  service = Service()

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def test_log_event(self, service_registry: MagicMock, *_: MagicMock) -> None :
    """Test logging events."""
    self._execute_logging_tests(
      method = lambda : self.service.LogEvent(MagicMock(), MagicMock()),
      logging_object = DbEvent.objects,
      logging_method = 'log_event',
    )
    service_registry.add_service.assert_called()

  def test_log_http_request(self, *_: MagicMock) -> None :
    """Test logging requests."""
    self._execute_logging_tests(
      method = lambda : self.service.LogHttpRequest(MagicMock(), MagicMock()),
      logging_object = DbHttpRequest.objects,
      logging_method = 'log_request',
    )

  def test_log_system_http_request(self, *_: MagicMock) -> None :
    """Test logging system HTTP requests."""
    self._execute_logging_tests(
      method = lambda : self.service.LogSystemHttpRequest(MagicMock(), MagicMock()),
      logging_object = DbHttpRequest.objects,
      logging_method = 'log_system_request',
    )

  def test_log_http_response(self, *_: MagicMock) -> None :
    """Test logging responses."""
    self._execute_logging_tests(
      method = lambda : self.service.LogHttpRequestResponse(MagicMock(), MagicMock()),
      logging_object = DbHttpRequest.objects,
      logging_method = 'log_response',
    )

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def test_log_grpc_request(self, service_registry: MagicMock, *_: MagicMock) -> None :
    """Test logging requests."""
    self._execute_logging_tests(
      method = lambda : self.service.LogGrpcRequest(MagicMock(), MagicMock()),
      logging_object = DbGrpcRequest.objects,
      logging_method = 'log_request',
    )
    service_registry.add_call.assert_called()

  def test_log_grpc_response(self, *_: MagicMock) -> None :
    """Test logging responses."""
    with patch.object(DbGrpcRequest.objects, 'log_response') as logging_grpc_request:
      with patch.object(DbHttpRequest.objects, 'add_child_duration') as logging_http_request:
        with patch.object(DbQuery.objects, 'log_queries') as logging_query:
          # Prepare data.
          now = datetime.now().replace(tzinfo = timezone.utc)
          logging_grpc_request.return_value = DbGrpcRequest()
          logging_grpc_request.return_value.to_grpc_request_response = MagicMock()
          logging_grpc_request.return_value.save = MagicMock()
          logging_query.return_value = [ DbQuery() ]
          logging_query.return_value[0].reported_start = now
          logging_query.return_value[0].reported_end = now + timedelta(days = 1)
          # Execute test.
          self.service.LogGrpcResponse(MagicMock(), MagicMock())
          # Assert result.
          logging_http_request.assert_called_once()
          logging_grpc_request.assert_called_once()
          logging_query.assert_called_once()
          logging_grpc_request.return_value.save.assert_called_once_with()

  def test_log_error(self, *_: MagicMock) -> None :
    """Test logging events."""
    self._execute_logging_tests(
      method = lambda : self.service.LogError(MagicMock(), MagicMock()),
      logging_object = DbError.objects,
      logging_method = 'log_error',
    )

  def _execute_logging_tests(
      self, *,
      method: Callable[[], Any],
      logging_object: Any,
      logging_method: str,
  ) -> None :
    """Execute all typical logging tests."""
    for test in [
        self._execute_successful_logging_test,
        self._execute_logging_test_with_parsing_error,
    ]:
      with self.subTest(test = test.__name__):
        with patch.object(logging_object, logging_method) as logging:
          test(method = method, logging = logging)  # type: ignore[operator]  # pylint: disable=no-value-for-parameter

  def _execute_successful_logging_test(
      self, *,
      method: Callable[[], Any],
      logging: MagicMock,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = Metadata()
    # Execute test.
    method()
    # Assert result.
    logging.assert_called_once()

  # noinspection PyUnusedLocal
  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def _execute_logging_test_with_parsing_error(
      self,
      _: MagicMock,
      *,
      method: Callable[[], Any],
      logging: MagicMock,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    expected_result = Metadata()
    expected_result.meta_logging_errors = 'some parsing errors'
    logging.return_value = expected_result
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(expected_result.meta_logging_errors, context.exception.private_details)
