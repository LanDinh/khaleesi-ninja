"""Interceptor to handle state of requests."""

# Python.
from typing import Callable, Any
from uuid import uuid4

# Django.
from django.conf import settings

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.logging.queryLogger import queryLogger
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.state import STATE


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class RequestStateServerInterceptor(ServerInterceptor):
  """Interceptor to handle state of requests."""

  def khaleesiIntercept(  # pylint: disable=inconsistent-return-statements
      self, *,
      executableMethod: Callable[[Any, ServicerContext], Any],
      request         : Any,
      context         : ServicerContext,
      rawMethod       : str,
  ) -> Any :
    """Handle the state of requests."""
    STATE.reset()  # Always start with a clean state.
    try:
      with queryLogger():
        STATE.request.grpcCaller.requestId = str(uuid4())
        # Process request data.
        _, _, service, method = self.processMethodName(raw = rawMethod)
        STATE.request.grpcCaller.service = service
        STATE.request.grpcCaller.method  = method

        upstream = self.getUpstreamRequest(request = request)
        STATE.request.httpCaller.requestId = upstream.httpCaller.requestId
        if upstream.user.id:
          STATE.request.user.id = upstream.user.id
        STATE.request.user.type = upstream.user.type

        # Continue execution.
        response = executableMethod(request, context)
        STATE.reset()  # Always clean up afterwards.
        return response
    except KhaleesiException as exception:
      self._handleException(context = context, exception = exception)
    except Exception as exception:  # pylint: disable=broad-except
      newException = MaskingInternalServerException(exception = exception)
      self._handleException(context = context, exception = newException)

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


def instantiateRequestStateInterceptor() -> RequestStateServerInterceptor :
  """Instantiate the request state interceptor."""
  return RequestStateServerInterceptor()
