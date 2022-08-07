"""Test the gRPC server."""

# Python.
import threading
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.settings.definition import StructuredLoggingMethod
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import Event


@patch('khaleesi.core.grpc.server.HEALTH_METRIC')
@patch('khaleesi.core.grpc.server.MetricInitializer')
@patch('khaleesi.core.grpc.server.ChannelManager')
@patch('khaleesi.core.grpc.server.server')
@patch('khaleesi.core.grpc.server.LumberjackStub')
@patch('khaleesi.core.grpc.server.LOGGER')
class ServerTestCase(SimpleTestCase):
  """Test the gRPC server."""

  def test_initialization_success(self, *_: MagicMock) -> None :
    """Test initialization success."""
    # Execute test & assert result.
    Server()

  def test_initialization_failure(
      self,
      logger: MagicMock,
      lumberjack_stub: MagicMock,
      grpc_server: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test initialization failure."""
    # Prepare data.
    grpc_server.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      Server()
    # Assert result.
    self.assert_server_state_event(
      action = Event.Action.ActionType.START,
      result = Event.Action.ResultType.FATAL,
      lumberjack_stub = lumberjack_stub
    )
    logger.fatal.assert_called_once()

  def test_sigterm_success(
      self,
      logger: MagicMock,
      lumberjack_stub: MagicMock,
      grpc_server: MagicMock,
      channel_manager: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test sigterm success."""
    # Prepare data.
    server = Server()
    event = threading.Event()
    grpc_server.return_value.stop.return_value = event
    lumberjack_stub.reset_mock()
    logger.reset_mock()
    # Execute test.
    event.set()
    server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self.assert_server_state_event(
      action = Event.Action.ActionType.END,
      result = Event.Action.ResultType.SUCCESS,
      lumberjack_stub = lumberjack_stub
    )
    logger.info.assert_called_once()
    channel_manager.return_value.close_all_channels.assert_called_once_with()

  def test_sigterm_failure(
      self,
      logger: MagicMock,
      lumberjack_stub: MagicMock,
      grpc_server: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test sigterm failure."""
    # Prepare data.
    server = Server()
    grpc_server.return_value.stop.side_effect = Exception('test')
    lumberjack_stub.reset_mock()
    # Execute test.
    with self.assertRaises(Exception):
      server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self.assert_server_state_event(
      action = Event.Action.ActionType.END,
      result = Event.Action.ResultType.FATAL,
      lumberjack_stub = lumberjack_stub
    )
    logger.fatal.assert_called_once()

  def test_sigterm_timeout(
      self,
      logger: MagicMock,
      lumberjack_stub: MagicMock,
      grpc_server: MagicMock,
      channel_manager: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test sigterm timeout."""
    # Prepare data.
    server = Server()
    event = threading.Event()
    grpc_server.return_value.stop.return_value = event
    lumberjack_stub.reset_mock()
    # Execute test.
    server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self.assert_server_state_event(
      action = Event.Action.ActionType.END,
      result = Event.Action.ResultType.ERROR,
      lumberjack_stub = lumberjack_stub
    )
    logger.error.assert_called_once()
    channel_manager.return_value.close_all_channels.assert_called_once_with()

  # noinspection PyUnusedLocal
  def test_start(  # pylint: disable=unused-argument
      self,
      logger: MagicMock,
      lumberjack_stub: MagicMock,
      grpc_server: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test that server start works correctly."""
    # Prepare data.
    server = Server()
    # Execute test.
    server.start()
    # Assert result.
    grpc_server.return_value.start.assert_called_once_with()
    grpc_server.return_value.wait_for_termination.assert_called_once_with()
    self.assert_server_state_event(
      action = Event.Action.ActionType.START,
      result = Event.Action.ResultType.SUCCESS,
      lumberjack_stub = lumberjack_stub
    )

  # noinspection PyUnusedLocal
  def test_start_failure(  # pylint: disable=unused-argument
      self,
      logger: MagicMock,
      lumberjack_stub: MagicMock,
      grpc_server: MagicMock,
      *_: MagicMock,
  ) -> None :
    """Test that server start works correctly."""
    # Prepare data.
    server = Server()
    grpc_server.return_value.start.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      server.start()
    # Assert result.
    self.assert_server_state_event(
      action = Event.Action.ActionType.START,
      result = Event.Action.ResultType.FATAL,
      lumberjack_stub = lumberjack_stub
    )

  @patch.dict('khaleesi.core.grpc.server.khaleesi_settings', {
      'CORE': { 'STRUCTURED_LOGGING_METHOD': StructuredLoggingMethod.GRPC },
      'GRPC': { 'HANDLERS': [ 'some.invalid.import' ], 'THREADS': 13, 'PORT': 1337 },
      'CONSTANTS': { 'GRPC_SERVER': { 'NAME': 'grpc-server', 'LIFECYCLE': 'lifecycle' } },
  })
  def test_add_invalid_handler(self, *_: MagicMock) -> None :
    """Test that invalid handlers raise ImportErrors."""
    # Execute test & assert result.
    with self.assertRaises(ImportError):
      Server()

  def assert_server_state_event(
      self, *,
      action: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
      lumberjack_stub: MagicMock
  ) -> None :
    """Assert the result."""
    lumberjack_stub.return_value.LogEvent.assert_called_once()
    event: Event = lumberjack_stub.return_value.LogEvent.call_args.args[0]
    self.assertEqual(event.action.crud_type, action)
    self.assertEqual(event.action.result   , result)
