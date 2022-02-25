"""Server interceptor utility."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext
from grpc_interceptor import ServerInterceptor as GrpcServerInterceptor

# khaleesi.ninja.
from khaleesi.core.interceptors.util import Interceptor


class ServerInterceptor(Interceptor, GrpcServerInterceptor):
  """Server interceptor utility."""

  khaleesi_intercept: Callable  # type: ignore[type-arg]

  def intercept(
      self,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      method_name: str,
  ) -> Any :
    """Intercept the method call."""
    _, _, service_name, method_name = self.process_method_name(raw = method_name)
    return self.khaleesi_intercept(
      method       = method,
      request      = request,
      context      = context,
      service_name = service_name,
      method_name  = method_name,
    )
