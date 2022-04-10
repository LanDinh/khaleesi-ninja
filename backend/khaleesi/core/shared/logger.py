"""Global logger."""

# Python.
import logging
from typing import Dict

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE


logger = logging.getLogger('khaleesi')


class Logger:
  """Global logger."""

  def __init__(self) -> None :
    logging.basicConfig()

  def debug(self, *, message: str) -> None :
    """Debug log."""
    logger.debug(message, extra = self._extra())

  def info(self, *, message: str) -> None :
    """Info log."""
    logger.info(message, extra = self._extra())

  def warning(self, *, message: str) -> None :
    """Warning log."""
    logger.warning(message, extra = self._extra())

  def error(self, *, message: str) -> None :
    """Error log."""
    logger.error(message, extra = self._extra())

  def fatal(self, *, message: str) -> None :
    """Fatal log."""
    logger.fatal(message, extra = self._extra())

  @staticmethod
  def _extra() -> Dict[str, str] :
    return {
        'request_id': str(STATE.request_id) if hasattr(STATE, 'request_id') else 'system'
    }


LOGGER = Logger()
