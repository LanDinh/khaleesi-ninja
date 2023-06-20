"""Interceptor to log incoming requests."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.shared.singleton import SINGLETON


class LoggingServerInterceptor(ServerInterceptor):
  """Interceptor to log requests."""

  def khaleesi_intercept(
      self, *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      **_: Any,
  ) -> Any :
    """Log the incoming request."""

    SINGLETON.structured_logger.log_grpc_request(
      upstream_request = self.get_upstream_request(request = request),
    )

    try:
      response = method(request, context)
      SINGLETON.structured_logger.log_grpc_response(status = StatusCode.OK)
      return response
    except KhaleesiException as exception:
      self._handle_exception(exception = exception)
      raise
    except Exception as exception:
      new_exception = MaskingInternalServerException(exception = exception)
      self._handle_exception(exception = new_exception)
      raise new_exception from exception

  def _handle_exception(self, *, exception: KhaleesiException) -> None :
    """Properly handle the exception."""
    SINGLETON.structured_logger.log_error(exception = exception)
    SINGLETON.structured_logger.log_grpc_response(status = exception.status)


def instantiate_logging_interceptor() -> LoggingServerInterceptor:
  """Instantiate the logging interceptor."""
  return LoggingServerInterceptor()
