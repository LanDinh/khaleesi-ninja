"""Per-request state."""

# Python.
import threading
from dataclasses import dataclass


@dataclass
class State:
  """Per-request state."""
  request_id: int

STATE: State = threading.local()  # type: ignore[assignment]
