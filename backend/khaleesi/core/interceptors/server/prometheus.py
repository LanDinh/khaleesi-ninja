"""Interceptor to collect prometheus metrics."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.exceptions import KhaleesiException
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.metrics.requests import INCOMING_REQUESTS
from khaleesi.proto.core_pb2 import RequestMetadata


class PrometheusServerInterceptor(ServerInterceptor):
  """Interceptor to collect prometheus metrics."""

  @staticmethod
  def khaleesi_intercept(  # pylint: disable=no-self-use
      *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      service_name: str,
      method_name: str,
  ) -> Any :
    """Collect the prometheus metrics."""
    labels = { 'grpc_service': service_name, 'grpc_method': method_name }
    if hasattr(request, 'request_metadata'):
      metadata: RequestMetadata = request.request_metadata
    else:
      metadata = RequestMetadata()
    try:
      response = method(request, context)
      INCOMING_REQUESTS.inc(status = StatusCode.OK, request_metadata = metadata, **labels)
      return response
    except KhaleesiException as exception:
      INCOMING_REQUESTS.inc(status = exception.status, request_metadata = metadata, **labels)
      raise exception from None
    except Exception as exception:
      INCOMING_REQUESTS.inc(status = StatusCode.UNKNOWN, request_metadata = metadata, **labels)
      raise exception from None
