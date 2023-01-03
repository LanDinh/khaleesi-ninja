"""Test the gRPC server command."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.management.commands.khaleesi_migrate import Command


@patch('khaleesi.management.commands.khaleesi_migrate.DjangoMigrateCommand')
class GrpcServerTestCase(SimpleTestCase):
  """Test the gRPC server command."""

  command = Command()

  def test_khaleesi_handle(self, django_migrate: MagicMock) -> None :
    """Test the handle method."""
    # Execute test.
    self.command.khaleesi_handle()
    # Assert result.
    django_migrate.handle.assert_called_once()
