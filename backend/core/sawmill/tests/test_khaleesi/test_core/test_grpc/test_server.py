"""Test the gRPC server."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import Event


@patch('khaleesi.core.grpc.server.HEALTH_METRIC')
@patch('khaleesi.core.grpc.server.ChannelManager')
@patch('khaleesi.core.grpc.server.server')
class ServerTestCase(SimpleTestCase):
  """Test the gRPC server."""

  def test_db_logging(self, grpc_server: MagicMock, *_: MagicMock) -> None :
    """Test initialization failure."""
    # Prepare data.
    db_module = MagicMock()
    grpc_server.side_effect = Exception('test')
    # Execute test.
    with patch.dict('sys.modules', { 'microservice.models': db_module }):
      with self.assertRaises(Exception):
        Server()
    # Assert result.
    db_module.Event.objects.log_event.called_once()
    event: Event = db_module.Event.objects.log_event.call_args.kwargs['grpc_event']
    self.assertEqual(event.action.crud_type, Event.Action.ActionType.START)
    self.assertEqual(event.action.result   , Event.Action.ResultType.FATAL)
