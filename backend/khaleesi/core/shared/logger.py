"""Global logger."""

# Python.
import logging
from enum import Enum
from typing import Dict

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE


logger = logging.getLogger('khaleesi')


class LogLevel(Enum):
  """Log levels."""
  DEBUG   = 0
  INFO    = 1
  WARNING = 2
  ERROR   = 3
  FATAL   = 4


class Logger:
  """Global logger."""

  def __init__(self) -> None :
    logging.basicConfig()

  def log(self, message: str, *, loglevel: LogLevel) -> None :
    """Log to a variable log level."""
    if loglevel == LogLevel.DEBUG:
      self.debug(message)
    if loglevel == LogLevel.INFO:
      self.info(message)
    if loglevel == LogLevel.WARNING:
      self.warning(message)
    if loglevel == LogLevel.ERROR:
      self.error(message)
    if loglevel == LogLevel.FATAL:
      self.fatal(message)

  def debug(self, message: str) -> None :
    """Debug log."""
    logger.debug(message, extra = self._extra())

  def info(self, message: str) -> None :
    """Info log."""
    logger.info(message, extra = self._extra())

  def warning(self, message: str) -> None :
    """Warning log."""
    logger.warning(message, extra = self._extra())

  def error(self, message: str) -> None :
    """Error log."""
    logger.error(message, extra = self._extra())

  def fatal(self, message: str) -> None :
    """Fatal log."""
    logger.fatal(message, extra = self._extra())

  def _extra(self) -> Dict[str, str] :
    return { 'request_id': STATE.request.id }


LOGGER = Logger()
