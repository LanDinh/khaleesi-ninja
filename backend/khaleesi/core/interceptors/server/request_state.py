"""Interceptor to handle state of requests."""

# Python.
from abc import ABC, abstractmethod
from typing import Callable, Any
from uuid import uuid4

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.logging.query_logger import query_logger
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.core.logging.structured_logger import StructuredLogger
from khaleesi.proto.core_pb2 import RequestMetadata


class BaseRequestStateServerInterceptor(ServerInterceptor, ABC):
  """Interceptor to handle state of requests."""

  # noinspection PyUnusedLocal
  def __init__(self, *, structured_logger: StructuredLogger) -> None :
    """Initialize the RequestStateServerInterceptor."""

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
      with query_logger():
        STATE.request.request_id = str(uuid4())
        # Process request data.
        _, _, service_name, method_name = self.process_method_name(raw = method_name)
        STATE.request.grpc_service = service_name
        STATE.request.grpc_method  = method_name

        upstream = self.get_upstream_request(request = request)
        self.set_backgate_request_id(upstream = upstream)
        if upstream.user.id:
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

  @abstractmethod
  def set_backgate_request_id(self, *, upstream: RequestMetadata) -> None :
    """Set the backgate request id."""

  def _handle_exception(
      self, *,
      context  : ServicerContext,
      exception: KhaleesiException,
  ) -> None :
    """Properly handle the exception."""
    STATE.reset()  # Always clean up afterwards.
    context.abort(code = exception.status, details = exception.to_json())


class RequestStateServerInterceptor(BaseRequestStateServerInterceptor):
  """RequestStateServerInterceptor that reads the ID from the request metadata."""

  def set_backgate_request_id(self, *, upstream: RequestMetadata) -> None :
    """Set the backgate request id."""
    if upstream.caller.backgate_request_id:
      STATE.request.backgate_request_id = upstream.caller.backgate_request_id
