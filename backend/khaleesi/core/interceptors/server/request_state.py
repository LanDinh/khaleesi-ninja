"""Interceptor to handle state of requests."""

# Python.
from typing import Callable, Any
from uuid import uuid4

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.state import STATE, UserType


class RequestStateServerInterceptor(ServerInterceptor):
  """Interceptor to handle state of requests."""

  def khaleesi_intercept(  # pylint: disable=inconsistent-return-statements
      self, *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      method_name: str,
  ) -> Any :
    """Handle the state of requests."""
    STATE.reset()  # Always start with a clean state.
    try:
      STATE.request.request_id = str(uuid4())
      # Process request data.
      _, _, service_name, method_name = self.process_method_name(raw = method_name)
      STATE.request.grpc_service = service_name
      STATE.request.grpc_method  = method_name

      upstream = self.get_upstream_request(request = request)
      STATE.user.user_id = upstream.user.id
      STATE.user.type    = UserType(upstream.user.type)

      # Continue execution.
      response = method(request, context)
      STATE.reset()  # Always clean up afterwards.
      return response
    except KhaleesiException as exception:
      self._handle_exception(context = context, exception = exception)
    except Exception as exception:  # pylint: disable=broad-except
      new_exception = MaskingInternalServerException(exception = exception)
      self._handle_exception(context = context, exception = new_exception)

  def _handle_exception(
      self, *,
      context  : ServicerContext,
      exception: KhaleesiException,
  ) -> None :
    """Properly handle the exception."""
    STATE.reset()  # Always clean up afterwards.
    context.abort(code = exception.status, details = exception.to_json())
