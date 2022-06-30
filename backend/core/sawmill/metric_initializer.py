"""Metric utility."""

# khaleesi.ninja.
from microservice.models.service_registry import SERVICE_REGISTRY


class MetricInitializer:
  """Collect info for initializing metrics."""

  def __init__(self) -> None :
    SERVICE_REGISTRY.reload()
