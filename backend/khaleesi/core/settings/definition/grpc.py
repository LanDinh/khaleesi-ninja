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
  BACKGATE_LOGGING          : GrpcEventMethodNames  # log backgate requests initiated by the system.
  LIFECYCLE                 : GrpcEventMethodNames  # report changes in lifecycle for logging.
  INITIALIZE_REQUEST_METRICS: GrpcEventMethodNames  # fetch gRPC calls for metric initialization.


class GrpcLoggingServerInterceptor(TypedDict):
  """Configuration for the logging server interceptor."""

  STRUCTURED_LOGGER: str

class GrpcInterceptors(TypedDict):
  """Interceptor configuration."""

  LOGGING_SERVER_INTERCEPTOR: GrpcLoggingServerInterceptor


class Grpc(TypedDict):
  """gRPC configuration for khaleesi.ninja services."""

  PORT               : int
  THREADS            : int
  SERVER_METHOD_NAMES: GrpcServerMethodNames
  HANDLERS           : List[str]
  INTERCEPTORS       : GrpcInterceptors
