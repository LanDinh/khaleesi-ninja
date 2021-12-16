"""Interceptor to collect prometheus metrics."""

# Python.
from typing import Callable, Any

# gRPC.
from grpc import ServicerContext
from grpc_interceptor import ServerInterceptor

# Prometheus.
from prometheus_client import Counter  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long
from prometheus_client.registry import REGISTRY  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long


class PrometheusServerInterceptor(ServerInterceptor):
  """Interceptor to collect prometheus metrics."""

  def __init__(self) -> None :
    self._metrics = {
      'khaleesi_test_counter': Counter(
        'khaleesi_test_counter',
        'Some test counter',
        ['test_label'],
        registry = REGISTRY,
      )
    }
    self._metrics['khaleesi_test_counter'].labels(test_label = 'khaleesi')

  def intercept(
      self,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      method_name: str,
  ) -> Any :
    """Collect the prometheus metrics."""
    self._metrics['khaleesi_test_counter'].labels(test_label = 'khaleesi').inc()
    return method(request, context)
