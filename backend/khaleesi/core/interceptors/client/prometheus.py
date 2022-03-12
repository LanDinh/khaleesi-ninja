"""Interceptor to collect prometheus metrics."""

# Python.
import traceback
from typing import Callable, Any

# gRPC.
from grpc import StatusCode, Call
from grpc_interceptor import ClientCallDetails

# khaleesi.ninja.
from khaleesi.core.exceptions import UpstreamGrpcException
from khaleesi.core.interceptors.client.util import ClientInterceptor
from khaleesi.core.metrics.requests import OUTGOING_REQUESTS
from khaleesi.proto.core_pb2 import RequestMetadata


class PrometheusClientInterceptor(ClientInterceptor):
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
    """Collect the prometheus metrics."""
    peer = RequestMetadata()
    peer.caller.khaleesi_gate    = khaleesi_gate
    peer.caller.khaleesi_service = khaleesi_service
    peer.caller.grpc_service     = grpc_service
    peer.caller.grpc_method      = grpc_method
    if hasattr(request_or_iterator, 'request_metadata'):
      request_metadata: RequestMetadata = request_or_iterator.request_metadata
    else:
      request_metadata = RequestMetadata()
    response: Call = method(request_or_iterator, call_details)
    OUTGOING_REQUESTS.inc(status = response.code(), request = request_metadata, peer = peer)

    if response.code() == StatusCode.OK:
      return response
    raise UpstreamGrpcException(
      status = response.code(),
      private_details = self.exception_details(response)
    )

  @staticmethod
  def exception_details(response: Call) -> str :
    """Return a pretty-print of the exception."""
    if hasattr(response, 'exception') and response.exception and response.exception():  # type: ignore[attr-defined]  # pylint: disable=line-too-long
      return ''.join(traceback.format_exception(response.exception()))  # type: ignore[attr-defined]
    return response.details()
