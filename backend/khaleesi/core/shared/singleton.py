"""Per-request state."""

# Python.
import threading

# khaleesi.ninja.
from khaleesi.core.logging.structuredLogger import StructuredLogger, instantiateStructuredLogger


class Singleton(threading.local):
  """Per-request state."""

  structuredLogger: StructuredLogger

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.structuredLogger = instantiateStructuredLogger()


SINGLETON = Singleton()
