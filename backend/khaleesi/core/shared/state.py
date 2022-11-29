"""Per-request state."""

# Python.
import threading
from dataclasses import dataclass
from enum import Enum


class UserType(Enum):
  """Different types of users."""

  # Non human.
  UNKNOWN = 0
  SYSTEM  = 1

  # Human.
  ANONYMOUS     = 10
  AUTHENTICATED = 11
  PRIVILEGED    = 12


@dataclass
class Request:
  """Request meta."""
  id          : int = -1  # pylint: disable=invalid-name
  grpc_service: str = 'UNKNOWN'
  grpc_method : str = 'UNKNOWN'

@dataclass
class User:
  """User data."""
  id  : str      = 'UNKNOWN'  # pylint: disable=invalid-name
  type: UserType = UserType.UNKNOWN

class State(threading.local):
  """Per-request state."""

  request: Request
  user: User

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.reset()

  def reset(self) -> None :
    """Reset to default state."""
    self.request = Request()
    self.user = User()


STATE = State()
