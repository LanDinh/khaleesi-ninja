"""Interceptor to collect prometheus metrics."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.shared.state import STATE
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.metrics.requests import INCOMING_REQUESTS
from khaleesi.proto.core_pb2 import RequestMetadata


class PrometheusServerInterceptor(ServerInterceptor):
  """Interceptor to collect prometheus metrics."""

  def khaleesiIntercept(
      self, *,
      method : Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      **_    : Any,
  ) -> Any :
    """Collect the prometheus metrics."""
    requestMetadata = RequestMetadata()
    requestMetadata.grpcCaller.grpcService = STATE.request.grpcCaller.grpcService
    requestMetadata.grpcCaller.grpcMethod  = STATE.request.grpcCaller.grpcMethod
    if hasattr(request, 'requestMetadata'):
      peer: RequestMetadata = request.requestMetadata
      requestMetadata.user.id   = peer.user.id
      requestMetadata.user.type = peer.user.type
    else:
      peer = RequestMetadata()
    try:
      response = method(request, context)
      INCOMING_REQUESTS.inc(status = StatusCode.OK, request = requestMetadata, peer = peer)
      return response
    except KhaleesiException as exception:
      INCOMING_REQUESTS.inc(status = exception.status, request = requestMetadata, peer = peer)
      raise
    except Exception:
      INCOMING_REQUESTS.inc(status = StatusCode.UNKNOWN, request = requestMetadata, peer = peer)
      raise


def instantiatePrometheusInterceptor() -> PrometheusServerInterceptor :
  """Instantiate the prometheus interceptor."""
  return PrometheusServerInterceptor()
