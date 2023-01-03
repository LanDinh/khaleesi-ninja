"""Test the gRPC server command."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.management.commands.grpcserver import Command


@patch('khaleesi.management.commands.grpcserver.start_http_server')
@patch('khaleesi.management.commands.grpcserver.Server')
class GrpcServerTestCase(SimpleTestCase):
  """Test the gRPC server command."""

  command = Command()

  def test_khaleesi_handle(self, server: MagicMock, metrics_server: MagicMock) -> None :
    """Test the handle method."""
    # Execute test.
    self.command.khaleesi_handle()
    # Assert result.
    server.return_value.start.assert_called_once_with()
    metrics_server.assert_called_once()
