"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict, List, Dict


class GrpcEventMethodName(TypedDict):
  """Method names for event-causing gRPC methods."""

  METHOD: str
  TARGET: str


class GrpcServerMethodNames(TypedDict):
  """Method names for methods that are inherent to gRPC servers."""

  SERVICE_NAME              : str
  USER_ID                   : str
  MIGRATE                   : GrpcEventMethodName  # Migrate database changes.
  INITIALIZE                : GrpcEventMethodName  # Initialize server.
  LIFECYCLE                 : GrpcEventMethodName  # Report changes in lifecycle for logging.
  INITIALIZE_REQUEST_METRICS: GrpcEventMethodName  # Fetch gRPC calls for metric initialization.
  APP_SPECIFIC              : Dict[str, GrpcEventMethodName]  # Enable custom methods for each app.


class Grpc(TypedDict):
  """gRPC configuration for khaleesi.ninja apps."""

  PORT               : int
  THREADS            : int
  SHUTDOWN_GRACE_SECS: int
  SERVER_METHOD_NAMES: GrpcServerMethodNames
  HANDLERS           : List[str]
