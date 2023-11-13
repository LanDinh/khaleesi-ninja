"""Interceptor to log incoming requests."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.singleton.structured_logger import SINGLETON


class LoggingServerInterceptor(ServerInterceptor):
  """Interceptor to log requests."""

  def khaleesiIntercept(
      self, *,
      executableMethod: Callable[[Any, ServicerContext], Any],
      request         : Any,
      context         : ServicerContext,
      **_             : Any,
  ) -> Any :
    """Log the incoming request."""

    SINGLETON.structuredLogger.logGrpcRequest(
      upstreamRequest = self.getUpstreamRequest(request = request).grpcCaller,
    )

    try:
      response = executableMethod(request, context)
      SINGLETON.structuredLogger.logGrpcResponse(status = StatusCode.OK)
      return response
    except KhaleesiException as exception:
      self._handleException(exception = exception)
      raise
    except Exception as exception:
      newException = MaskingInternalServerException(exception = exception)
      self._handleException(exception = newException)
      raise newException from exception

  def _handleException(self, *, exception: KhaleesiException) -> None :
    """Properly handle the exception."""
    SINGLETON.structuredLogger.logError(exception = exception)
    SINGLETON.structuredLogger.logGrpcResponse(status = exception.status)


def instantiateLoggingInterceptor() -> LoggingServerInterceptor:
  """Instantiate the logging interceptor."""
  return LoggingServerInterceptor()
