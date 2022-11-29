"""Interceptor to handle state of requests."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.shared.state import STATE, UserType


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
    STATE.reset()  # Always start with a clean state.
    try:
      # Process request data.
      _, _, service_name, method_name = self.process_method_name(raw = method_name)
      upstream = self.get_upstream_request(request = request)

      STATE.request.grpc_service = service_name
      STATE.request.grpc_method  = method_name
      STATE.user.id   = upstream.user.id
      STATE.user.type = UserType(upstream.user.type)

      # Continue execution.
      response = method(request, context)
      STATE.reset()  # Always clean up afterwards.
      return response
    except Exception:
      STATE.reset()  # Always clean up afterwards.
      raise
