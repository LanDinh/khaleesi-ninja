"""Per-request state."""

# Python.
import threading

# khaleesi.ninja.
from khaleesi.core.logging.structured_logger import StructuredLogger, instantiate_structured_logger


class Singleton(threading.local):
  """Per-request state."""

  structured_logger: StructuredLogger

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.structured_logger = instantiate_structured_logger()


SINGLETON = Singleton()
