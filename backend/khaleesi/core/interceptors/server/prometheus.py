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

  def khaleesi_intercept(
      self, *,
      method  : Callable[[Any, ServicerContext], Any],
      request : Any,
      context : ServicerContext,
      **_     : Any,
  ) -> Any :
    """Collect the prometheus metrics."""
    request_metadata = RequestMetadata()
    request_metadata.caller.grpc_service = STATE.request.grpc_service
    request_metadata.caller.grpc_method  = STATE.request.grpc_method
    if hasattr(request, 'request_metadata'):
      peer: RequestMetadata = request.request_metadata
      request_metadata.user.id   = peer.user.id
      request_metadata.user.type = peer.user.type
    else:
      peer = RequestMetadata()
    try:
      response = method(request, context)
      INCOMING_REQUESTS.inc(status = StatusCode.OK, request = request_metadata, peer = peer)
      return response
    except KhaleesiException as exception:
      INCOMING_REQUESTS.inc(status = exception.status, request = request_metadata, peer = peer)
      raise
    except Exception:
      INCOMING_REQUESTS.inc(status = StatusCode.UNKNOWN, request = request_metadata, peer = peer)
      raise
