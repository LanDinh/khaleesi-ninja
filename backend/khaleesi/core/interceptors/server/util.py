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
      request_or_iterator: Any,
      context: ServicerContext,
      method_name: str,
  ) -> Any :
    """Intercept the method call."""
    if self.skip_interceptors(raw = method_name):
      return method(request_or_iterator, context)

    _, _, service_name, method_name = self.process_method_name(raw = method_name)
    return self.khaleesi_intercept(
      method       = method,
      request      = request_or_iterator,
      context      = context,
      service_name = service_name,
      method_name  = method_name,
    )
