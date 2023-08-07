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
from khaleesi.core.logging.textLogger import LOGGER


class LoggingClientInterceptor(ClientInterceptor):
  """Interceptor to collect prometheus metrics."""

  def khaleesiIntercept(
      self, *,
      executableMethod : Callable[[Any, ClientCallDetails], Any],
      requestOrIterator: Any,
      callDetails      : ClientCallDetails,
      site             : str,
      app              : str,
      service          : str,
      method           : str,
  ) -> Any :
    """Log data."""
    LOGGER.info(f'Calling {site}-{app}: {service}.{method}...')

    response: Call = executableMethod(requestOrIterator, callDetails)

    if response.code() == StatusCode.OK:
      LOGGER.info(f'Call to {site}-{app}: {service}.{method} was ok.')
      return response
    LOGGER.warning(f'Call to {site}-{app}: {service}.{method} returned {response.code()}.')
    raise UpstreamGrpcException(
      status         = response.code(),
      privateDetails = self.exceptionDetails(response = response)
    )

  def exceptionDetails(self, *, response: Call) -> str :
    """Return a pretty-print of the exception."""
    if hasattr(response, 'exception') and response.exception and response.exception():
      return ''.join(traceback.format_exception(response.exception()))
    return response.details()
