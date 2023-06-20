"""Test the structured logger."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.structured_logger import StructuredDbLogger


class TestStructuredDbLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredDbLogger()

  @patch('microservice.structured_logger.DbHttpRequest')
  def test_send_log_system_http_request(self, db_http_request: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    request = MagicMock()
    # Perform test.
    self.logger.send_log_system_http_request(http_request = request)
    # Assert result.
    db_http_request.objects.log_system_request.assert_called_once_with(grpc_request = request)

  @patch('microservice.structured_logger.DbHttpRequest')
  def test_send_log_http_request(self, db_http_request: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    request = MagicMock()
    # Perform test.
    self.logger.send_log_http_request(http_request = request)
    # Assert result.
    db_http_request.objects.log_request.assert_called_once_with(grpc_request = request)

  @patch('microservice.structured_logger.DbHttpRequest')
  def test_send_log_http_response(self, db_http_request: MagicMock) -> None :
    """Test sending a log response."""
    # Prepare data.
    response = MagicMock()
    # Perform test.
    self.logger.send_log_http_response(http_response = response)
    # Assert result.
    db_http_request.objects.log_response.assert_called_once_with(grpc_response = response)

  @patch('microservice.structured_logger.SERVICE_REGISTRY')
  @patch('microservice.structured_logger.DbGrpcRequest')
  def test_send_log_grpc_request(
      self,
      db_grpc_request : MagicMock,
      service_registry: MagicMock,
  ) -> None :
    """Test sending a log request."""
    # Prepare data.
    grpc_request = MagicMock()
    # Perform test.
    self.logger.send_log_grpc_request(grpc_request = grpc_request)
    # Assert result.
    db_grpc_request.objects.log_request.assert_called_once_with(grpc_request = grpc_request)
    service_registry.add_call.assert_called_once()

  @patch('microservice.structured_logger.DbQuery')
  @patch('microservice.structured_logger.DbGrpcRequest')
  @patch('microservice.structured_logger.DbHttpRequest')
  def test_send_log_grpc_response(
      self,
      db_http_request: MagicMock,
      db_grpc_request: MagicMock,
      db_query       : MagicMock,
  ) -> None :
    """Test sending a log response."""
    # Prepare data.
    response = MagicMock()
    # Perform test.
    self.logger.send_log_grpc_response(grpc_response = response)
    # Assert result.
    db_http_request.objects.add_child_duration.assert_called_once()
    db_grpc_request.objects.log_response.assert_called_once_with(grpc_response = response)
    db_grpc_request.objects.log_response.return_value.save.assert_called_once_with()
    db_query.objects.log_queries.assert_called_once()

  @patch('microservice.structured_logger.DbError')
  def test_send_log_error(self, db_error: MagicMock) -> None :
    """Test sending a log error."""
    # Prepare data.
    error = MagicMock()
    # Perform test.
    self.logger.send_log_error(error = error)
    # Assert result.
    db_error.objects.log_error.assert_called_once_with(grpc_error = error)

  @patch('microservice.structured_logger.DbEvent')
  def test_send_log_event(self, db_event: MagicMock) -> None :
    """Test sending a log event."""
    # Prepare data.
    event = MagicMock()
    # Perform test.
    self.logger.send_log_event(event = event)
    # Assert result.
    db_event.objects.log_event.assert_called_once_with(grpc_event = event)
