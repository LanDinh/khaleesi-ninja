"""Test import util."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.grpc.importUtil import importSetting, registerService
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.core.testUtil.testCase import SimpleTestCase


@patch('khaleesi.core.grpc.importUtil.LOGGER')
@patch('khaleesi.core.grpc.importUtil.import_string')
class ImportUtilTestcase(SimpleTestCase):
  """Test import util."""

  def testValidImportSetting(self, importString: MagicMock, *_: MagicMock) -> None :
    """Test valid import setting."""
    # Execute test.
    importSetting(name = 'name', fullyQualifiedName = 'some-valid-import')
    # Assert result.
    importString.assert_called_once()

  def testInvalidImportSetting(self, importString: MagicMock, *_: MagicMock) -> None :
    """Test invalid import setting."""
    # Prepare data.
    importString.side_effect = ImportError('error')
    # Execute test.
    with self.assertRaises(ProgrammingException):
      importSetting(name = 'name', fullyQualifiedName = 'some-invalid-import')
    # Assert result.
    importString.assert_called_once()

  def testValidRegisterService(self, importString: MagicMock, *_: MagicMock) -> None :
    """Test valid service registration."""
    # Prepare data.
    server = MagicMock()
    # Execute test.
    registerService(rawHandler = '', server = server)
    # Assert result.
    importString.assert_called_once()
    importString.return_value.registerService.assert_called_once_with(server)

  def testInvalidRegisterService(self, importString: MagicMock, *_: MagicMock) -> None :
    """Test invalid service registration."""
    # Prepare data.
    server = MagicMock()
    importString.side_effect = ImportError('error')
    # Execute test.
    with self.assertRaises(ProgrammingException):
      registerService(rawHandler = '', server = server)
    # Assert result.
    importString.assert_called_once()
    importString.return_value.registerService.assert_not_called()
