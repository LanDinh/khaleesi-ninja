"""Per-request state."""

from __future__ import annotations

# Python.
import threading
from typing import List

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import Query


class State(threading.local):
  """Per-request state."""

  request: RequestMetadata
  queries: List[Query]

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.reset()

  def copyFrom(self, *, request: RequestMetadata, queries: List[Query]) -> None :
    """Copy the state from somewhere else. Used for sharing state with a thread."""
    self.request.CopyFrom(request)
    for sourceQuery in queries:
      query = Query()
      query.CopyFrom(sourceQuery)
      self.queries.append(query)

  def reset(self) -> None :
    """Reset to default state."""
    self.request = RequestMetadata()
    self.request.httpCaller.requestId = 'UNKNOWN'
    self.request.grpcCaller.requestId   = 'system'
    self.request.user.id = 'UNKNOWN'
    self.request.user.type = User.UserType.UNKNOWN

    # Misc.
    self.queries = []


STATE = State()
