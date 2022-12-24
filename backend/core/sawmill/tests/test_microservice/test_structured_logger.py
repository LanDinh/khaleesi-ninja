"""Test the structured logger."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.structured_logger import StructuredDbLogger


class TestStructuredDbLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredDbLogger(channel_manager = MagicMock())

  @patch('microservice.structured_logger.DbBackgateRequest')
  def test_send_log_system_backgate_request(self, db_backgate_request: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    request = MagicMock()
    # Perform test.
    self.logger.send_log_system_backgate_request(backgate_request = request)
    # Assert result.
    db_backgate_request.objects.log_system_backgate_request.assert_called_once_with(
      grpc_backgate_request = request,
    )

  @patch('microservice.structured_logger.SERVICE_REGISTRY')
  @patch('microservice.structured_logger.DbRequest')
  def test_send_log_request(self, db_request: MagicMock, service_registry: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    request = MagicMock()
    # Perform test.
    self.logger.send_log_request(request = request)
    # Assert result.
    db_request.objects.log_request.assert_called_once_with(grpc_request = request)
    service_registry.add_call.assert_called_once()

  @patch('microservice.structured_logger.DbRequest')
  def test_send_log_response(self, db_request: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    response = MagicMock()
    # Perform test.
    self.logger.send_log_response(response = response)
    # Assert result.
    db_request.objects.log_response.assert_called_once_with(grpc_response = response)

  @patch('microservice.structured_logger.DbError')
  def test_send_log_error(self, db_error: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    error = MagicMock()
    # Perform test.
    self.logger.send_log_error(error = error)
    # Assert result.
    db_error.objects.log_error.assert_called_once_with(grpc_error = error)

  @patch('microservice.structured_logger.DbEvent')
  def test_send_log_event(self, db_event: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    event = MagicMock()
    # Perform test.
    self.logger.send_log_event(event = event)
    # Assert result.
    db_event.objects.log_event.assert_called_once_with(grpc_event = event)
