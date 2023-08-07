"""Server interceptor utility."""

# Python.
from typing import Callable, Any, cast

# gRPC.
from grpc import ServicerContext
from grpc_interceptor import ServerInterceptor as GrpcServerInterceptor

# khaleesi.ninja.
from khaleesi.core.interceptors.util import Interceptor
from khaleesi.proto.core_pb2 import RequestMetadata


class ServerInterceptor(Interceptor, GrpcServerInterceptor):
  """Server interceptor utility."""

  khaleesiIntercept: Callable  # type: ignore[type-arg]

  def intercept(
      self,
      method             : Callable[[Any, ServicerContext], Any],
      request_or_iterator: Any,
      context            : ServicerContext,
      method_name        : str,
  ) -> Any :
    """Intercept the method call."""
    if self.skipInterceptors(raw = method_name):
      return method(request_or_iterator, context)

    return self.khaleesiIntercept(
      executableMethod = method,
      request          = request_or_iterator,
      context          = context,
      rawMethod        = method_name,
    )

  def getUpstreamRequest(self, *, request: Any) -> RequestMetadata :
    """Get the upstream request."""
    if hasattr(request, 'requestMetadata'):
      return cast(RequestMetadata, request.requestMetadata)
    return RequestMetadata()
