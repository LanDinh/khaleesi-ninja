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
    khaleesiGate, khaleesiService, grpcService, grpcMethod = self.processMethodName(
      raw = call_details.method,
    )
    return self.khaleesiIntercept(
      method            = method,
      requestOrIterator = request_or_iterator,
      callDetails       = call_details,
      khaleesiGate      = self.stringOrUnknown(value = khaleesiGate),
      khaleesiService   = self.stringOrUnknown(value = khaleesiService),
      grpcService       = self.stringOrUnknown(value = grpcService),
      grpcMethod        = self.stringOrUnknown(value = grpcMethod),
    )
