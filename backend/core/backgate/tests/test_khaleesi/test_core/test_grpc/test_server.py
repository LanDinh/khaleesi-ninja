"""Test the gRPC server."""

# Python.
import threading
from unittest.mock import patch, MagicMock

# Django.
from django.conf import settings
from django.utils.module_loading import import_string

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event


khaleesi_ninja_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


@patch('khaleesi.core.grpc.server.LOGGER')
@patch('khaleesi.core.grpc.server.HEALTH_METRIC')
@patch('khaleesi.core.grpc.server.MetricInitializer')
@patch('khaleesi.core.grpc.server.ChannelManager')
@patch('khaleesi.core.grpc.server.server')
class ServerTestCase(SimpleTestCase):
  """Test the gRPC server."""

  def test_initialization_success(self, *_: MagicMock) -> None :
    """Test initialization success."""
    # Execute test & assert result.
    Server()

  @patch('khaleesi.core.grpc.server.import_string')
  def test_initialization_failure(
      self,
      import_string_mock: MagicMock,
      grpc_server       : MagicMock,
      *_                : MagicMock,
  ) -> None :
    """Test initialization failure."""
    # Prepare data.
    grpc_server.side_effect = Exception('test')
    structured_logger = self._mock_import_string(import_string_mock = import_string_mock)
    # Execute test.
    with self.assertRaises(Exception):
      Server()
    # Assert result.
    self._assert_server_state_event(
      action            = Event.Action.ActionType.START,
      result            = Event.Action.ResultType.FATAL,
      structured_logger = structured_logger
    )

  @patch('khaleesi.core.grpc.server.import_string')
  def test_sigterm_success(self,
      import_string_mock  : MagicMock,
      grpc_server         : MagicMock,
      channel_manager     : MagicMock,
      *_                  : MagicMock,
  ) -> None :
    """Test sigterm success."""
    # Prepare data.
    structured_logger = self._mock_import_string(import_string_mock = import_string_mock)
    server = Server()
    event = threading.Event()
    grpc_server.return_value.stop.return_value = event
    # Execute test.
    event.set()
    server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assert_server_state_event(
      action            = Event.Action.ActionType.END,
      result            = Event.Action.ResultType.SUCCESS,
      structured_logger = structured_logger,
    )
    channel_manager.return_value.close_all_channels.assert_called_once_with()

  @patch('khaleesi.core.grpc.server.import_string')
  def test_sigterm_failure(
      self,
      import_string_mock: MagicMock,
      grpc_server       : MagicMock,
      *_                : MagicMock,
  ) -> None :
    """Test sigterm failure."""
    # Prepare data.
    structured_logger = self._mock_import_string(import_string_mock = import_string_mock)
    server = Server()
    grpc_server.return_value.stop.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assert_server_state_event(
      action            = Event.Action.ActionType.END,
      result            = Event.Action.ResultType.FATAL,
      structured_logger = structured_logger,
    )

  @patch('khaleesi.core.grpc.server.import_string')
  def test_sigterm_timeout(
      self,
      import_string_mock: MagicMock,
      grpc_server       : MagicMock,
      channel_manager   : MagicMock,
      *_                : MagicMock,
  ) -> None :
    """Test sigterm timeout."""
    # Prepare data.
    structured_logger = self._mock_import_string(import_string_mock = import_string_mock)
    server = Server()
    event = threading.Event()
    grpc_server.return_value.stop.return_value = event
    # Execute test.
    server._handle_sigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assert_server_state_event(
      action            = Event.Action.ActionType.END,
      result            = Event.Action.ResultType.ERROR,
      structured_logger = structured_logger,
    )
    channel_manager.return_value.close_all_channels.assert_called_once_with()

  @patch('khaleesi.core.grpc.server.import_string')
  def test_start(
      self,
      import_string_mock: MagicMock,
      grpc_server       : MagicMock,
      *_                : MagicMock,
  ) -> None :
    """Test that server start works correctly."""
    # Prepare data.
    structured_logger = self._mock_import_string(import_string_mock = import_string_mock)
    server = Server()
    # Execute test.
    server.start()
    # Assert result.
    grpc_server.return_value.start.assert_called_once_with()
    grpc_server.return_value.wait_for_termination.assert_called_once_with()
    self._assert_server_state_event(
      action            = Event.Action.ActionType.START,
      result            = Event.Action.ResultType.SUCCESS,
      structured_logger = structured_logger,
    )

  @patch('khaleesi.core.grpc.server.import_string')
  def test_start_failure(
      self,
      import_string_mock: MagicMock,
      grpc_server       : MagicMock,
      *_                : MagicMock,
  ) -> None :
    """Test that server start fails correctly."""
    # Prepare data.
    structured_logger = self._mock_import_string(import_string_mock = import_string_mock)
    server = Server()
    grpc_server.return_value.start.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      server.start()
    # Assert result.
    self._assert_server_state_event(
      action            = Event.Action.ActionType.START,
      result            = Event.Action.ResultType.FATAL,
      structured_logger = structured_logger,
    )

  @patch.dict('khaleesi.core.grpc.server.khaleesi_settings', {
      'GRPC': {
          'THREADS': 13,
          'PORT': 1337,
          'SERVER_METHOD_NAMES': {
              'SERVICE_NAME': 'grpc-server',
              'USER_ID': 'grpc-server',
              'LIFECYCLE': {
                  'METHOD': 'lifecycle',
                  'TARGET': 'core.core.server',
              },
          },
          'HANDLERS': [ 'some.invalid.import' ],
          'INTERCEPTORS': {
              'LOGGING_SERVER_INTERCEPTOR': {
                  'STRUCTURED_LOGGER': 'khaleesi.core.shared.structured_logger.StructuredGrpcLogger'
              }
          }
      },
  })
  @patch('khaleesi.core.shared.structured_logger.LOGGER')
  def test_add_invalid_handler(self, *_: MagicMock) -> None :
    """Test that invalid handlers raise ImportErrors."""
    # Execute test & assert result.
    with self.assertRaises(ImportError):
      Server()

  def _mock_import_string(self, *, import_string_mock: MagicMock) -> MagicMock :
    """Return the structured logger, but don't mock the handlers."""
    structured_logger = MagicMock()
    import_string_mock.side_effect = \
      [ lambda **kwargs: structured_logger ] + \
      [
          import_string(f'{handler}.service_configuration')
          for handler in khaleesi_ninja_settings['GRPC']['HANDLERS']
      ]
    return structured_logger


  def _assert_server_state_event(
      self, *,
      action           : 'Event.Action.ActionType.V',
      result           : 'Event.Action.ResultType.V',
      structured_logger: MagicMock,
  ) -> None :
    """Assert the result."""
    structured_logger.log_system_event.assert_called_once()
    kwargs = structured_logger.log_system_event.call_args.kwargs
    self.assertEqual(kwargs['grpc_method'], 'LIFECYCLE')
    self.assertEqual(kwargs['owner'].type , User.UserType.SYSTEM)
    self.assertEqual(kwargs['action']     , action)
    self.assertEqual(kwargs['result']     , result)
