"""Interceptor to log incoming requests."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.logging.structured_logger import StructuredLogger


class LoggingServerInterceptor(ServerInterceptor):
  """Interceptor to log requests."""

  structured_logger: StructuredLogger

  def __init__(self, *, structured_logger: StructuredLogger) -> None :
    super().__init__()
    self.structured_logger = structured_logger

  def khaleesi_intercept(
      self, *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      **_: Any,
  ) -> Any :
    """Log the incoming request."""

    self.structured_logger.log_request(
      upstream_request = self.get_upstream_request(request = request),
    )

    try:
      response = method(request, context)
      self.structured_logger.log_response(status = StatusCode.OK)
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
    self.structured_logger.log_error(exception = exception)
    self.structured_logger.log_response(status = exception.status)
