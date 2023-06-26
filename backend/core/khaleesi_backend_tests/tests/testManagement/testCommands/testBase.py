"""Test the gRPC server command."""

# Python.
from unittest.mock import patch, MagicMock
from typing import Any

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import StdoutWriter, StderrWriter
from khaleesi.core.testUtil.testCase import SimpleTestCase
# noinspection PyProtectedMember
from khaleesi.management.commands._base import BaseCommand


class Command(BaseCommand):
  """Test command."""

  mock = MagicMock()

  def khaleesiHandle(self, *args: Any, **options: Any) -> None :
    """Handle the command."""
    self.mock()


@patch('khaleesi.management.commands._base.queryLogger')
class BaseCommandTestCase(SimpleTestCase):
  """Test the gRPC server command."""

  command = Command()

  def testHandle(self, queryLogger: MagicMock) -> None :
    """Test the handle method."""
    # Execute test.
    self.command.handle()
    # Assert result.
    self.assertIsInstance(self.command.stdout._out, StdoutWriter)  # pylint: disable=protected-access
    self.assertIsInstance(self.command.stderr._out, StderrWriter)  # pylint: disable=protected-access
    queryLogger.assert_called_once_with()
    self.command.mock.assert_called_once_with()
