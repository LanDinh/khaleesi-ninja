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
  """Grpc configuration for khaleesi.ninja services."""

  PORT     : int
  HANDLERS : List[str]
  THREADS  : int

class Monitoring(TypedDict):
  """Grpc configuration for khaleesi.ninja services."""

  PORT : int


class StructuredLoggingMethod(Enum):
  """Methods to log structured logs."""

  GRPC     = 1
  DATABASE = 2

class Core(TypedDict):
  """Logging configuration for khaleesi.ninja services."""

  STRUCTURED_LOGGING_METHOD: StructuredLoggingMethod


class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""

  METADATA   : Metadata
  GRPC       : Grpc
  MONITORING : Monitoring
  CORE       : Core
