"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict, List


class GrpcEventMethodNames(TypedDict):
  """Method names for event-causing gRPC methods."""

  METHOD: str
  TARGET: str


class GrpcServerMethodNames(TypedDict):
  """Method names for methods that are inherent to gRPC servers."""

  SERVICE_NAME              : str
  USER_ID                   : str
  MIGRATE                   : GrpcEventMethodNames  # Migrate database changes.
  INITIALIZE                : GrpcEventMethodNames  # Initialize server.
  LIFECYCLE                 : GrpcEventMethodNames  # Report changes in lifecycle for logging.
  INITIALIZE_REQUEST_METRICS: GrpcEventMethodNames  # Fetch gRPC calls for metric initialization.


class GrpcServerInterceptor(TypedDict):
  """Configuration for the logging server interceptor."""

  NAME: str

class GrpcInterceptors(TypedDict):
  """Interceptor configuration."""

  STRUCTURED_LOGGER: GrpcServerInterceptor


class Grpc(TypedDict):
  """gRPC configuration for khaleesi.ninja apps."""

  PORT               : int
  THREADS            : int
  SHUTDOWN_GRACE_SECS: int
  SERVER_METHOD_NAMES: GrpcServerMethodNames
  HANDLERS           : List[str]
  INTERCEPTORS       : GrpcInterceptors
