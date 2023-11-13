"""Per-request state."""

# Python.
import threading

# khaleesi.ninja.
from khaleesi.core.batch.broom import BaseBroom, instantiateBroom


class Singleton(threading.local):
  """Per-request state."""

  broom           : BaseBroom

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.broom = instantiateBroom()


SINGLETON = Singleton()
