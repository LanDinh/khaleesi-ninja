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

  def khaleesiIntercept(
      self, *,
      method           : Callable[[Any, ClientCallDetails], Any],
      requestOrIterator: Any,
      callDetails      : ClientCallDetails,
      khaleesiGate     : str,
      khaleesiService  : str,
      grpcService      : str,
      grpcMethod       : str,
  ) -> Any :
    """Collect the prometheus metrics."""
    peer = RequestMetadata()
    peer.grpcCaller.khaleesiGate    = khaleesiGate
    peer.grpcCaller.khaleesiService = khaleesiService
    peer.grpcCaller.grpcService     = grpcService
    peer.grpcCaller.grpcMethod      = grpcMethod
    if hasattr(requestOrIterator, 'requestMetadata'):
      requestMetadata: RequestMetadata = requestOrIterator.requestMetadata
    else:
      requestMetadata = RequestMetadata()
    response: Call = method(requestOrIterator, callDetails)
    OUTGOING_REQUESTS.inc(status = response.code(), request = requestMetadata, peer = peer)

    return response
