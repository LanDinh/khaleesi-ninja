"""Per-request state."""

# Python.
import threading
from dataclasses import dataclass

@dataclass
class Request:
  """Request meta."""
  id          : int = -1  # pylint: disable=invalid-name
  service_name: str = 'UNKNOWN'
  method_name : str = 'UNKNOWN'

class State(threading.local):
  """Per-request state."""

  request: Request

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.reset()

  def reset(self) -> None :
    """Reset to default state."""
    self.request = Request()


STATE = State()
