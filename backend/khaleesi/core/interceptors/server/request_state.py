"""Interceptor to handle state of requests."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.shared.state import STATE, Request

class RequestStateServerInterceptor(ServerInterceptor):
  """Interceptor to handle state of requests."""

  def khaleesi_intercept(
      self, *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      method_name: str,
  ) -> Any :
    """Handle the state of requests."""
    self._clean_state()  # Always start with a clean state.
    try:
      # Process request data.
      _, _, service_name, method_name = self.process_method_name(raw = method_name)
      STATE.request.service_name = service_name
      STATE.request.method_name  = method_name
      # Continue execution.
      response = method(request, context)
      self._clean_state()  # Always clean up afterwards.
      return response
    except Exception:
      self._clean_state()  # Always clean up afterwards.
      raise

  def _clean_state(self) -> None :
    """Produce a clean state."""
    STATE.request = Request(id = -1, service_name = 'UNKNOWN', method_name = 'UNKNOWN')
