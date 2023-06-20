"""Per-request state."""

# Python.
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict

# Django.
from django.db import connections


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
  http_request_id: str = 'UNKNOWN'
  grpc_request_id: str = 'system'
  grpc_service   : str = 'UNKNOWN'
  grpc_method    : str = 'UNKNOWN'

@dataclass
class User:
  """User data."""
  user_id: str      = 'UNKNOWN'
  type   : UserType = UserType.UNKNOWN

@dataclass
class Query:
  """Query data."""
  query_id  : str
  raw       : str
  start     : datetime
  end       : datetime = datetime.max.replace(tzinfo = timezone.utc)

class State(threading.local):
  """Per-request state."""

  request: Request
  user   : User
  queries: Dict[str, List[Query]]

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.reset()

  def reset(self) -> None :
    """Reset to default state."""
    self.request = Request()
    self.user    = User()
    self.queries = {}
    for connection in connections:
      self.queries[connection] = []


STATE = State()
