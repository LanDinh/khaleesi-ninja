"""Per-request state."""

# Python.
import threading
from dataclasses import dataclass

@dataclass
class Request:
  """Request meta."""
  id          : int  # pylint: disable=invalid-name
  service_name: str
  method_name : str

@dataclass
class State:
  """Per-request state."""
  request: Request

STATE: State = threading.local()  # type: ignore[assignment]
