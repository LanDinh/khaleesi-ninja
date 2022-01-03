"""khaleesi.ninja settings definition."""

# Python.
from enum import Enum
from typing import TypedDict, List


class KhaleesiNinjaServiceType(Enum):
  """Types of khaleesi.ninja services."""

  BACKGATE = 1
  MICRO    = 2

class KhaleesiNinjaMetadata(TypedDict):
  """Metadata for khaleesi.ninja services."""

  GATE    : str
  SERVICE : str
  TYPE    : KhaleesiNinjaServiceType
  VERSION : str

class KhaleesiNinjaGrpc(TypedDict):
  """Grpc configuration for khaleesi.ninja services."""

  PORT     : int
  HANDLERS : List[str]

class KhaleesiNinjaMonitoring(TypedDict):
  """Grpc configuration for khaleesi.ninja services."""

  PORT : int


class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""

  METADATA   : KhaleesiNinjaMetadata
  GRPC       : KhaleesiNinjaGrpc
  MONITORING : KhaleesiNinjaMonitoring
