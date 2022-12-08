"""Test the global logger."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.logger import LOGGER
from khaleesi.core.test_util.test_case import SimpleTestCase


@patch('khaleesi.core.shared.logger.logger')
class LoggerTestCase(SimpleTestCase):
  """Test the global logger."""

  logger = LOGGER
  message = 'test'

  def test_debug(self, logger: MagicMock) -> None :
    """Test debug logging."""
    # Execute test.
    self.logger.debug(self.message)
    # Assert result.
    logger.debug.assert_called_once()
    self.assertEqual(self.message, logger.debug.call_args.args[0])

  def test_info(self, logger: MagicMock) -> None :
    """Test info logging."""
    # Execute test.
    self.logger.info(self.message)
    # Assert result.
    logger.info.assert_called_once()
    self.assertEqual(self.message, logger.info.call_args.args[0])

  def test_warning(self, logger: MagicMock) -> None :
    """Test warning logging."""
    # Execute test.
    self.logger.warning(self.message)
    # Assert result.
    logger.warning.assert_called_once()
    self.assertEqual(self.message, logger.warning.call_args.args[0])

  def test_error(self, logger: MagicMock) -> None :
    """Test error logging."""
    # Execute test.
    self.logger.error(self.message)
    # Assert result.
    logger.error.assert_called_once()
    self.assertEqual(self.message, logger.error.call_args.args[0])

  def test_fatal(self, logger: MagicMock) -> None :
    """Test fatal logging."""
    # Execute test.
    self.logger.fatal(self.message)
    # Assert result.
    logger.fatal.assert_called_once()
    self.assertEqual(self.message, logger.fatal.call_args.args[0])
