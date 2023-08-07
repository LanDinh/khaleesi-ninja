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
      executableMethod : Callable[[Any, ClientCallDetails], Any],
      requestOrIterator: Any,
      callDetails      : ClientCallDetails,
      site             : str,
      app              : str,
      service          : str,
      method           : str,
  ) -> Any :
    """Collect the prometheus metrics."""
    peer = RequestMetadata()
    peer.grpcCaller.site    = site
    peer.grpcCaller.app     = app
    peer.grpcCaller.service = service
    peer.grpcCaller.method  = method
    if hasattr(requestOrIterator, 'requestMetadata'):
      requestMetadata: RequestMetadata = requestOrIterator.requestMetadata
    else:
      requestMetadata = RequestMetadata()
    response: Call = executableMethod(requestOrIterator, callDetails)
    OUTGOING_REQUESTS.inc(status = response.code(), request = requestMetadata, peer = peer)

    return response
