"""Server interceptor utility."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext
from grpc_interceptor import ServerInterceptor as GrpcServerInterceptor


class ServerInterceptor(GrpcServerInterceptor):
  """Server interceptor utility."""

  khaleesi_intercept: Callable  # type: ignore[type-arg]

  def __init__(self) -> None :
    """Initialize interceptor."""

  def intercept(
      self,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      method_name: str,
  ) -> Any :
    """Intercept the method call."""
    method_name_parts = method_name.split('/')
    grpc_service_name = method_name_parts[1] if len(method_name_parts) > 1 else ''
    grpc_method_name  = method_name_parts[2] if len(method_name_parts) > 2 else ''
    return self.khaleesi_intercept(
      method       = method,
      request      = request,
      context      = context,
      service_name = self.string_or_unknown(value = grpc_service_name),
      method_name  = self.string_or_unknown(value = grpc_method_name),
    )

  @staticmethod
  def string_or_unknown(*, value: str) -> str :
    """Either return the value, or UNKNOWN if empty."""
    if value:
      return value
    return 'UNKNOWN'
