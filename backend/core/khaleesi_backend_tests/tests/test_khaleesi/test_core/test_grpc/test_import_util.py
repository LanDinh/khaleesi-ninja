"""Test import util."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.grpc.import_util import import_setting, register_service
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.core.test_util.test_case import SimpleTestCase


@patch('khaleesi.core.grpc.import_util.LOGGER')
@patch('khaleesi.core.grpc.import_util.import_string')
class ImportUtilTestcase(SimpleTestCase):
  """Test import util."""

  def test_valid_import_setting(self, import_string: MagicMock, *_: MagicMock) -> None :
    """Test valid import setting."""
    # Execute test.
    import_setting(name = 'name', fully_qualified_name = 'some-valid-import')
    # Assert result.
    import_string.assert_called_once()

  def test_invalid_import_setting(self, import_string: MagicMock, *_: MagicMock) -> None :
    """Test invalid import setting."""
    # Prepare data.
    import_string.side_effect = ImportError('error')
    # Execute test.
    with self.assertRaises(ProgrammingException):
      import_setting(name = 'name', fully_qualified_name = 'some-invalid-import')
    # Assert result.
    import_string.assert_called_once()

  def test_valid_register_service(self, import_string: MagicMock, *_: MagicMock) -> None :
    """Test valid service registration."""
    # Prepare data.
    server = MagicMock()
    # Execute test.
    register_service(raw_handler = '', server = server)
    # Assert result.
    import_string.assert_called_once()
    import_string.return_value.register_service.assert_called_once_with(server)

  def test_invalid_register_service(self, import_string: MagicMock, *_: MagicMock) -> None :
    """Test valid service registration."""
    # Prepare data.
    server = MagicMock()
    import_string.side_effect = ImportError('error')
    # Execute test.
    with self.assertRaises(ProgrammingException):
      register_service(raw_handler = '', server = server)
    # Assert result.
    import_string.assert_called_once()
    import_string.return_value.register_service.assert_not_called()
