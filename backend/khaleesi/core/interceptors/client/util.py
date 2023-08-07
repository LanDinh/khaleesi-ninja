"""Server interceptor utility."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc_interceptor import ClientInterceptor as GrpcClientInterceptor, ClientCallDetails

# khaleesi.ninja.
from khaleesi.core.interceptors.util import Interceptor


class ClientInterceptor(Interceptor, GrpcClientInterceptor):
  """Server interceptor utility."""

  khaleesiIntercept: Callable  # type: ignore[type-arg]

  def intercept(  # type: ignore[override]
      self,
      method             : Callable[[Any, ClientCallDetails], Any],
      request_or_iterator: Any,
      call_details       : ClientCallDetails,
  ) -> Any :
    """Intercept the method call."""
    site, app, service, methodName = self.processMethodName(
      raw = call_details.method,
    )
    return self.khaleesiIntercept(
      executableMethod  = method,
      requestOrIterator = request_or_iterator,
      callDetails       = call_details,
      site              = self.stringOrUnknown(value = site),
      app               = self.stringOrUnknown(value = app),
      service           = self.stringOrUnknown(value = service),
      method            = self.stringOrUnknown(value = methodName),
    )
