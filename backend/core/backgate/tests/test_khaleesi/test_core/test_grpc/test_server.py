"""Test the gRPC server."""

# Python.
import threading
from unittest.mock import patch, MagicMock

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import TimeoutException
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event


khaleesi_ninja_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA

@patch('khaleesi.core.grpc.server.reflection')
@patch('khaleesi.core.grpc.server.register_service')
@patch('khaleesi.core.grpc.server.instantiate_logging_interceptor')
@patch('khaleesi.core.grpc.server.instantiate_prometheus_interceptor')
@patch('khaleesi.core.grpc.server.instantiate_request_state_interceptor')
@patch('khaleesi.core.grpc.server.LOGGER')
@patch('khaleesi.core.grpc.server.HEALTH_METRIC')
@patch('khaleesi.core.grpc.server.MetricInitializer')
@patch('khaleesi.core.grpc.server.CHANNEL_MANAGER')
@patch('khaleesi.core.grpc.server.SINGLETON')
@patch('khaleesi.core.grpc.server.server')
class ServerTestCase(SimpleTestCase):
  """Test the gRPC server."""

  def test_initialization_success(self, *_: MagicMock) -> None :
    """Test initialization success."""
    # Execute test & assert result.
    Server(start_backgate_request_id = 'backgate-request', initialize_request_id = 'request-id')

  def test_initialization_failure(
      self,
      grpc_server: MagicMock,
      singleton  : MagicMock,
      *_         : MagicMock,
  ) -> None :
    """Test initialization failure."""
    # Prepare data.
    grpc_server.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      Server(start_backgate_request_id = 'backgate-request', initialize_request_id = 'request-id')
    # Assert result.
    self._assert_server_state_event(
      action    = Event.Action.ActionType.START,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )

  def test_sigterm_success(self,
      grpc_server    : MagicMock,
      singleton      : MagicMock,
      channel_manager: MagicMock,
      *_             : MagicMock,
  ) -> None :
    """Test sigterm success."""
    # Prepare data.
    server = Server(
      start_backgate_request_id = 'backgate-request',
      initialize_request_id = 'request-id',
    )
    event = threading.Event()
    grpc_server.return_value.stop.return_value = event
    # Execute test.
    event.set()
    server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assert_server_state_event(
      action    = Event.Action.ActionType.END,
      result    = Event.Action.ResultType.SUCCESS,
      singleton = singleton,
    )
    singleton.structured_logger.log_system_backgate_request.assert_called_once()
    singleton.structured_logger.log_system_request.assert_called_once()
    singleton.structured_logger.log_response.assert_called_once()
    singleton.structured_logger.log_backgate_response.assert_called_once()
    channel_manager.close_all_channels.assert_called_once_with()

  def test_sigterm_failure(
      self,
      grpc_server    : MagicMock,
      singleton      : MagicMock,
      channel_manager: MagicMock,
      *_             : MagicMock,
  ) -> None :
    """Test sigterm failure."""
    # Prepare data.
    server = Server(
      start_backgate_request_id = 'backgate-request',
      initialize_request_id = 'request-id',
    )
    grpc_server.return_value.stop.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assert_server_state_event(
      action    = Event.Action.ActionType.END,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )
    singleton.structured_logger.log_system_backgate_request.assert_called_once()
    singleton.structured_logger.log_system_request.assert_called_once()
    singleton.structured_logger.log_response.assert_called_once()
    singleton.structured_logger.log_backgate_response.assert_called_once()
    channel_manager.close_all_channels.assert_called_once_with()

  def test_sigterm_timeout(
      self,
      grpc_server    : MagicMock,
      singleton      : MagicMock,
      channel_manager: MagicMock,
      *_             : MagicMock,
  ) -> None :
    """Test sigterm timeout."""
    # Prepare data.
    server = Server(
      start_backgate_request_id = 'backgate-request',
      initialize_request_id = 'request-id',
    )
    event = threading.Event()
    grpc_server.return_value.stop.return_value = event
    # Execute test.
    with self.assertRaises(TimeoutException):
      server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assert_server_state_event(
      action    = Event.Action.ActionType.END,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )
    singleton.structured_logger.log_system_backgate_request.assert_called_once()
    singleton.structured_logger.log_system_request.assert_called_once()
    singleton.structured_logger.log_response.assert_called_once()
    singleton.structured_logger.log_backgate_response.assert_called_once()
    channel_manager.close_all_channels.assert_called_once_with()

  def test_start(self, grpc_server: MagicMock, singleton: MagicMock, *_: MagicMock) -> None :
    """Test that server start works correctly."""
    # Prepare data.
    server = Server(
      start_backgate_request_id = 'backgate-request',
      initialize_request_id = 'request-id',
    )
    # Execute test.
    server.start(start_request_id = 'request-id')
    # Assert result.
    grpc_server.return_value.start.assert_called_once_with()
    grpc_server.return_value.wait_for_termination.assert_called_once_with()
    self._assert_server_state_event(
      action    = Event.Action.ActionType.START,
      result    = Event.Action.ResultType.SUCCESS,
      singleton = singleton,
    )

  def test_start_failure(
      self,
      grpc_server: MagicMock,
      singleton  : MagicMock,
      *_         : MagicMock,
  ) -> None :
    """Test that server start fails correctly."""
    # Prepare data.
    server = Server(
      start_backgate_request_id = 'backgate-request',
      initialize_request_id = 'request-id',
    )
    grpc_server.return_value.start.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      server.start(start_request_id = 'request-id')
    # Assert result.
    self._assert_server_state_event(
      action    = Event.Action.ActionType.START,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )


  def _assert_server_state_event(
      self, *,
      action   : 'Event.Action.ActionType.V',
      result   : 'Event.Action.ResultType.V',
      singleton: MagicMock,
  ) -> None :
    """Assert the result."""
    kwargs = singleton.structured_logger.log_system_event.call_args.kwargs
    self.assertEqual(kwargs['grpc_method']       , 'LIFECYCLE')
    self.assertEqual(kwargs['owner'].type        , User.UserType.SYSTEM)
    self.assertEqual(kwargs['action']            , action)
    self.assertEqual(kwargs['result']            , result)
    self.assertEqual(kwargs['logger_send_metric'], True)
