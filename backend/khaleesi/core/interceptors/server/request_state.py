"""Interceptor to handle state of requests."""

# Python.
from abc import ABC, abstractmethod
from typing import Callable, Any, cast
from uuid import uuid4

# Django.
from django.conf import settings

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.grpc.import_util import import_setting
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.logging.query_logger import query_logger
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.proto.core_pb2 import RequestMetadata


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class BaseRequestStateServerInterceptor(ServerInterceptor, ABC):
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
    LOGGER.log(exception.to_json(), loglevel = exception.loglevel)
    LOGGER.log(exception.stacktrace, loglevel = exception.loglevel)
    STATE.reset()  # Always clean up afterwards.
    context.abort(code = exception.status, details = exception.to_json())


class RequestStateServerInterceptor(BaseRequestStateServerInterceptor):
  """RequestStateServerInterceptor that reads the ID from the request metadata."""

  def set_backgate_request_id(self, *, upstream: RequestMetadata) -> None :
    """Set the backgate request id."""
    if upstream.caller.backgate_request_id:
      STATE.request.backgate_request_id = upstream.caller.backgate_request_id


def instantiate_request_state_interceptor() -> BaseRequestStateServerInterceptor :
  """Instantiate the request state interceptor."""
  LOGGER.info('Importing request state interceptor...')
  return cast(BaseRequestStateServerInterceptor, import_setting(
    name                 = 'request state interceptor',
    fully_qualified_name = khaleesi_settings['GRPC']['INTERCEPTORS']['REQUEST_STATE']['NAME'],
  ))
