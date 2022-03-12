"""Server interceptor utility."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc_interceptor import ClientInterceptor as GrpcClientInterceptor, ClientCallDetails

# khaleesi.ninja.
from khaleesi.core.interceptors.util import Interceptor


class ClientInterceptor(Interceptor, GrpcClientInterceptor):
  """Server interceptor utility."""

  khaleesi_intercept: Callable  # type: ignore[type-arg]

  def intercept(  # type: ignore[override]
      self,
      method: Callable[[Any, ClientCallDetails], Any],
      request_or_iterator: Any,
      call_details: ClientCallDetails,
  ) -> Any :
    """Intercept the method call."""
    khaleesi_gate, khaleesi_service, grpc_service, grpc_method = self.process_method_name(
      raw = call_details.method,
    )
    return self.khaleesi_intercept(
      method              = method,
      request_or_iterator = request_or_iterator,
      call_details        = call_details,
      khaleesi_gate       = self.string_or_unknown(value = khaleesi_gate),
      khaleesi_service    = self.string_or_unknown(value = khaleesi_service),
      grpc_service        = self.string_or_unknown(value = grpc_service),
      grpc_method         = self.string_or_unknown(value = grpc_method),
    )
