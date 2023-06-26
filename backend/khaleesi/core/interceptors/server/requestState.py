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
from khaleesi.core.grpc.importUtil import importSetting
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.logging.queryLogger import queryLogger
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.proto.core_pb2 import RequestMetadata


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class BaseRequestStateServerInterceptor(ServerInterceptor, ABC):
  """Interceptor to handle state of requests."""

  def khaleesiIntercept(  # pylint: disable=inconsistent-return-statements
      self, *,
      method    : Callable[[Any, ServicerContext], Any],
      request   : Any,
      context   : ServicerContext,
      methodName: str,
  ) -> Any :
    """Handle the state of requests."""
    STATE.reset()  # Always start with a clean state.
    try:
      with queryLogger():
        STATE.request.grpcRequestId = str(uuid4())
        # Process request data.
        _, _, serviceName, methodName = self.processMethodName(raw = methodName)
        STATE.request.grpcService = serviceName
        STATE.request.grpcMethod  = methodName

        upstream = self.getUpstreamRequest(request = request)
        self.setHttpRequestId(upstream = upstream)
        if upstream.user.id:
          STATE.user.userId = upstream.user.id
        STATE.user.type = UserType(upstream.user.type)

        # Continue execution.
        response = method(request, context)
        STATE.reset()  # Always clean up afterwards.
        return response
    except KhaleesiException as exception:
      self._handleException(context = context, exception = exception)
    except Exception as exception:  # pylint: disable=broad-except
      newException = MaskingInternalServerException(exception = exception)
      self._handleException(context = context, exception = newException)

  @abstractmethod
  def setHttpRequestId(self, *, upstream: RequestMetadata) -> None :
    """Set the HTTP request id."""

  def _handleException(
      self, *,
      context  : ServicerContext,
      exception: KhaleesiException,
  ) -> None :
    """Properly handle the exception."""
    LOGGER.log(exception.toJson(), loglevel = exception.loglevel)
    LOGGER.log(exception.stacktrace, loglevel = exception.loglevel)
    STATE.reset()  # Always clean up afterwards.
    context.abort(code = exception.status, details = exception.toJson())


class RequestStateServerInterceptor(BaseRequestStateServerInterceptor):
  """RequestStateServerInterceptor that reads the ID from the request metadata."""

  def setHttpRequestId(self, *, upstream: RequestMetadata) -> None :
    """Set the HTTP request id."""
    if upstream.caller.httpRequestId:
      STATE.request.httpRequestId = upstream.caller.httpRequestId


def instantiateRequestStateInterceptor() -> BaseRequestStateServerInterceptor :
  """Instantiate the request state interceptor."""
  LOGGER.info('Importing request state interceptor...')
  return cast(BaseRequestStateServerInterceptor, importSetting(
    name               = 'request state interceptor',
    fullyQualifiedName = khaleesiSettings['GRPC']['INTERCEPTORS']['REQUEST_STATE']['NAME'],
  ))
