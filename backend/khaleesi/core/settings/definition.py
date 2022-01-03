"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict, List


class KhaleesiNinjaGrpc(TypedDict):
  """Grpc configuration for khaleesi.ninja services."""

  PORT     : int
  HANDLERS : List[str]

class KhaleesiNinjaMonitoring(TypedDict):
  """Grpc configuration for khaleesi.ninja services."""

  PORT : int


class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""

  GRPC       : KhaleesiNinjaGrpc
  MONITORING : KhaleesiNinjaMonitoring
