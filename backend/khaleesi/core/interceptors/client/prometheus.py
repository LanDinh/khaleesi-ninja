"""Interceptor to collect prometheus metrics."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import Call
from grpc_interceptor import ClientCallDetails

# khaleesi.ninja.
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
    peer.caller.khaleesiGate    = khaleesi_gate
    peer.caller.khaleesiService = khaleesi_service
    peer.caller.grpcService     = grpc_service
    peer.caller.grpcMethod      = grpc_method
    if hasattr(request_or_iterator, 'requestMetadata'):
      request_metadata: RequestMetadata = request_or_iterator.requestMetadata
    else:
      request_metadata = RequestMetadata()
    response: Call = method(request_or_iterator, call_details)
    OUTGOING_REQUESTS.inc(status = response.code(), request = request_metadata, peer = peer)

    return response
