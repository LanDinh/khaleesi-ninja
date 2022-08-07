"""khaleesi.ninja settings definition."""

# Python.
from enum import Enum
from typing import TypedDict, List


class ServiceType(Enum):
  """Types of khaleesi.ninja services."""

  BACKGATE = 1
  MICRO    = 2

class Metadata(TypedDict):
  """Metadata for khaleesi.ninja services."""

  GATE    : str
  SERVICE : str
  TYPE    : ServiceType
  VERSION : str


class Grpc(TypedDict):
  """gRPC configuration for khaleesi.ninja services."""

  PORT     : int
  HANDLERS : List[str]
  THREADS  : int


class Monitoring(TypedDict):
  """Monitoring configuration for khaleesi.ninja services."""

  PORT : int


class StructuredLoggingMethod(Enum):
  """Methods to log structured logs."""

  GRPC     = 1
  DATABASE = 2

class Core(TypedDict):
  """Core configuration for khaleesi.ninja services."""

  STRUCTURED_LOGGING_METHOD: StructuredLoggingMethod


class GrpcDict(TypedDict):
  """Dictionary representing a gRPC service."""

  NAME                       : str
  LIFECYCLE                  : str  # report changes in lifecycle for logging
  INITIALIZE_REQUEST_METRICS : str  # fetch gRPC calls for metric initialization

class Constants(TypedDict):
  """Constants shared by everything."""

  GRPC_SERVER : GrpcDict


class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""

  METADATA   : Metadata
  GRPC       : Grpc
  MONITORING : Monitoring
  CORE       : Core
  CONSTANTS  : Constants
