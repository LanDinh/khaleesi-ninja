"""Interceptor to log data."""

# Python.
import traceback
from typing import Callable, Any

# gRPC.
from grpc import StatusCode, Call
from grpc_interceptor import ClientCallDetails

# khaleesi.ninja.
from khaleesi.core.interceptors.client.util import ClientInterceptor
from khaleesi.core.shared.exceptions import UpstreamGrpcException
from khaleesi.core.shared.logger import LOGGER


class LoggingClientInterceptor(ClientInterceptor):
  """Interceptor to collect prometheus metrics."""

  def khaleesi_intercept(
      self, *,
      method             : Callable[[Any, ClientCallDetails], Any],
      request_or_iterator: Any,
      call_details       : ClientCallDetails,
      khaleesi_gate      : str,
      khaleesi_service   : str,
      grpc_service       : str,
      grpc_method        : str,
  ) -> Any :
    """Log data."""
    LOGGER.info(f'Calling {khaleesi_gate}.{khaleesi_service}{grpc_service}.{grpc_method}...')

    response: Call = method(request_or_iterator, call_details)

    if response.code() == StatusCode.OK:
      LOGGER.info(f'Call to {khaleesi_gate}.{khaleesi_service}{grpc_service}.{grpc_method} was ok.')
      return response
    LOGGER.warning(
      f'Call to {khaleesi_gate}.{khaleesi_service}{grpc_service}.{grpc_method} was not ok.',
    )
    raise UpstreamGrpcException(
      status = response.code(),
      private_details = self.exception_details(response = response)
    )

  def exception_details(self, *, response: Call) -> str :
    """Return a pretty-print of the exception."""
    if hasattr(response, 'exception') and response.exception and response.exception():  # type: ignore[attr-defined]  # pylint: disable=line-too-long
      return ''.join(traceback.format_exception(response.exception()))  # type: ignore[attr-defined]
    return response.details()
