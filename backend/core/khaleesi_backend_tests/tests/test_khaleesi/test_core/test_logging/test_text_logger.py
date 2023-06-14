"""Test the global logger."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LOGGER, LogLevel, STDOUT_WRITER, STDERR_WRITER
from khaleesi.core.test_util.test_case import SimpleTestCase


@patch('khaleesi.core.logging.text_logger.logger')
class LoggerTestCase(SimpleTestCase):
  """Test the text logger."""

  message = 'test'

  def test_debug(self, logger: MagicMock) -> None :
    """Test debug logging."""
    # Execute test.
    LOGGER.debug(self.message)
    # Assert result.
    logger.debug.assert_called_once()
    self.assertEqual(self.message, logger.debug.call_args.args[0])

  def test_info(self, logger: MagicMock) -> None :
    """Test info logging."""
    # Execute test.
    LOGGER.info(self.message)
    # Assert result.
    logger.info.assert_called_once()
    self.assertEqual(self.message, logger.info.call_args.args[0])

  def test_warning(self, logger: MagicMock) -> None :
    """Test warning logging."""
    # Execute test.
    LOGGER.warning(self.message)
    # Assert result.
    logger.warning.assert_called_once()
    self.assertEqual(self.message, logger.warning.call_args.args[0])

  def test_error(self, logger: MagicMock) -> None :
    """Test error logging."""
    # Execute test.
    LOGGER.error(self.message)
    # Assert result.
    logger.error.assert_called_once()
    self.assertEqual(self.message, logger.error.call_args.args[0])

  def test_fatal(self, logger: MagicMock) -> None :
    """Test fatal logging."""
    # Execute test.
    LOGGER.fatal(self.message)
    # Assert result.
    logger.fatal.assert_called_once()
    self.assertEqual(self.message, logger.fatal.call_args.args[0])

  def test_debug_indirect(self, logger: MagicMock) -> None :
    """Test debug logging."""
    # Execute test.
    LOGGER.log(self.message, loglevel = LogLevel.DEBUG)
    # Assert result.
    logger.debug.assert_called_once()
    self.assertEqual(self.message, logger.debug.call_args.args[0])

  def test_info_indirect(self, logger: MagicMock) -> None :
    """Test info logging."""
    # Execute test.
    LOGGER.log(self.message, loglevel = LogLevel.INFO)
    # Assert result.
    logger.info.assert_called_once()
    self.assertEqual(self.message, logger.info.call_args.args[0])

  def test_warning_indirect(self, logger: MagicMock) -> None :
    """Test warning logging."""
    # Execute test.
    LOGGER.log(self.message, loglevel = LogLevel.WARNING)
    # Assert result.
    logger.warning.assert_called_once()
    self.assertEqual(self.message, logger.warning.call_args.args[0])

  def test_error_indirect(self, logger: MagicMock) -> None :
    """Test error logging."""
    # Execute test.
    LOGGER.log(self.message, loglevel = LogLevel.ERROR)
    # Assert result.
    logger.error.assert_called_once()
    self.assertEqual(self.message, logger.error.call_args.args[0])

  def test_fatal_indirect(self, logger: MagicMock) -> None :
    """Test fatal logging."""
    # Execute test.
    LOGGER.log(self.message, loglevel = LogLevel.FATAL)
    # Assert result.
    logger.fatal.assert_called_once()
    self.assertEqual(self.message, logger.fatal.call_args.args[0])


@patch('khaleesi.core.logging.text_logger.logger')
class StdoutWriterTestCase(SimpleTestCase):
  """Test the stdout writer."""

  message = 'test'

  def test_write(self, logger: MagicMock) -> None :
    """Test the stdout writer."""
    # Execute test.
    STDOUT_WRITER.write(self.message)
    # Assert result.
    logger.info.assert_called_once()
    self.assertEqual(self.message, logger.info.call_args.args[0])


@patch('khaleesi.core.logging.text_logger.logger')
class StderrWriterTestCase(SimpleTestCase):
  """Test the stdout writer."""

  message = 'test'

  def test_write(self, logger: MagicMock) -> None :
    """Test the stdout writer."""
    # Execute test.
    STDERR_WRITER.write(self.message)
    # Assert result.
    logger.error.assert_called_once()
    self.assertEqual(self.message, logger.error.call_args.args[0])
