"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict, List


class Batch(TypedDict):
  """Method names for event-causing gRPC methods."""

  TARGET_TYPE: str
