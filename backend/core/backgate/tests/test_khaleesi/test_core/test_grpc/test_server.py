"""Test the gRPC server."""

# Python.
import threading
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import Event


@patch('khaleesi.core.grpc.server.HEALTH_METRIC')
@patch('khaleesi.core.grpc.server.ChannelManager')
@patch('khaleesi.core.grpc.server.server')
@patch('khaleesi.core.grpc.server.LumberjackStub')
class ServerTestCase(SimpleTestCase):
  """Test the gRPC server."""

  def test_initialization_success(self, lumberjack_stub: MagicMock, *_: MagicMock) -> None :
    """Test initialization success."""
    # Execute test.
    Server()
    # Assert result.
    self.assert_result(
      action = Event.Action.ActionType.START,
      result = Event.Action.ResultType.SUCCESS,
      lumberjack_stub = lumberjack_stub
    )

  def test_initialization_failure(
      self,
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
    self.assert_result(
      action = Event.Action.ActionType.START,
      result = Event.Action.ResultType.ERROR,
      lumberjack_stub = lumberjack_stub
    )

  def test_sigterm_success(
      self,
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
    # Execute test.
    event.set()
    server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self.assert_result(
      action = Event.Action.ActionType.END,
      result = Event.Action.ResultType.SUCCESS,
      lumberjack_stub = lumberjack_stub
    )
    channel_manager.return_value.close_all_channels.assert_called_once_with()

  def test_sigterm_failure(
      self,
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
    self.assert_result(
      action = Event.Action.ActionType.END,
      result = Event.Action.ResultType.ERROR,
      lumberjack_stub = lumberjack_stub
    )

  def test_sigterm_timeout(
      self,
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
    self.assert_result(
      action = Event.Action.ActionType.END,
      result = Event.Action.ResultType.WARNING,
      lumberjack_stub = lumberjack_stub
    )
    channel_manager.return_value.close_all_channels.assert_called_once_with()

  # noinspection PyMethodMayBeStatic,PyUnusedLocal
  def test_start(self, lumberjack_stub: MagicMock, grpc_server: MagicMock, *_: MagicMock) -> None :  # pylint: disable=unused-argument,no-self-use
    """Test that server start works correctly."""
    # Prepare data.
    server = Server()
    # Execute test.
    server.start()
    # Assert result.
    grpc_server.return_value.start.assert_called_once_with()
    grpc_server.return_value.wait_for_termination.assert_called_once_with()

  def assert_result(
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
