"""Interceptor to collect prometheus metrics."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.exceptions import KhaleesiException
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.metrics.requests import OUTGOING_REQUESTS
from khaleesi.proto.core_pb2 import RequestMetadata


class PrometheusServerInterceptor(ServerInterceptor):
  """Interceptor to collect prometheus metrics."""

  def khaleesi_intercept(  # pylint: disable=no-self-use
      self, *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      service_name: str,
      method_name: str,
  ) -> Any :
    """Collect the prometheus metrics."""
    metadata: RequestMetadata = request.request_metadata
    labels = {
        'grpc_service'          : service_name,
        'grpc_method'           : method_name,
        'peer_khaleesi_gate'    : metadata.caller.khaleesi_gate,
        'peer_khaleesi_service' : metadata.caller.khaleesi_service,
        'peer_grpc_service'     : metadata.caller.grpc_service,
        'peer_grpc_method'      : metadata.caller.grpc_method,
    }
    user = metadata.user.type
    try:
      response = method(request, context)
      OUTGOING_REQUESTS.inc(status = StatusCode.OK, user = user, **labels)
      return response
    except KhaleesiException as exception:
      OUTGOING_REQUESTS.inc(status = exception.status, user = user, **labels)
      raise exception from None
    except Exception as exception:
      OUTGOING_REQUESTS.inc(status = StatusCode.UNKNOWN, user = user, **labels)
      raise exception from None
