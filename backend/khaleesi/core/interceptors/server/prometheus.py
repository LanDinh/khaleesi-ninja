"""Interceptor to collect prometheus metrics."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.exceptions import KhaleesiException
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.metrics.requests import INCOMING_REQUESTS
from khaleesi.proto.core_pb2 import RequestMetadata, User


class PrometheusServerInterceptor(ServerInterceptor):
  """Interceptor to collect prometheus metrics."""

  def khaleesi_intercept(
      self, *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      service_name: str,
      method_name: str,
  ) -> Any :
    """Collect the prometheus metrics."""
    if hasattr(request, 'request_metadata'):
      metadata: RequestMetadata = request.request_metadata
      labels = {
          'grpc_service'         : service_name,
          'grpc_method'          : method_name,
          'peer_khaleesi_gate'   : self.string_or_unknown(value = metadata.caller.khaleesi_gate),
          'peer_khaleesi_service': self.string_or_unknown(value = metadata.caller.khaleesi_service),
          'peer_grpc_service'    : self.string_or_unknown(value = metadata.caller.grpc_service),
          'peer_grpc_method'     : self.string_or_unknown(value = metadata.caller.grpc_method),
      }
      user = metadata.user.type
    else:
      labels = {
          'grpc_service'         : service_name,
          'grpc_method'          : method_name,
          'peer_khaleesi_gate'   : 'UNKNOWN',
          'peer_khaleesi_service': 'UNKNOWN',
          'peer_grpc_service'    : 'UNKNOWN',
          'peer_grpc_method'     : 'UNKNOWN',
      }
      user = User.UserType.UNKNOWN
    try:
      with INCOMING_REQUESTS.track_in_progress(user = user, **labels):
        response = method(request, context)
      INCOMING_REQUESTS.inc(status = StatusCode.OK, user = user, **labels)
      return response
    except KhaleesiException as exception:
      INCOMING_REQUESTS.inc(status = exception.status, user = user, **labels)
      raise exception from None
    except Exception as exception:
      INCOMING_REQUESTS.inc(status = StatusCode.UNKNOWN, user = user, **labels)
      raise exception from None
