"""Monitoring metrics utility."""

# Python.
from enum import Enum
from functools import partial
from typing import TypeVar, Generic, Dict, Type, List, Any

# Django.
from django.conf import settings

# Prometheus.
from prometheus_client import Gauge  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long
from prometheus_client.metrics import MetricWrapperBase  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long
from prometheus_client.registry import REGISTRY  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaMetadata


khaleesi_settings: KhaleesiNinjaMetadata = settings.KHALEESI_NINJA['METADATA']
server_labels = {
    'khaleesi_gate'    : khaleesi_settings['GATE'],
    'khaleesi_service' : khaleesi_settings['SERVICE'],
    'khaleesi_type'    : khaleesi_settings['TYPE'].name.lower(),
    'khaleesi_version' : khaleesi_settings['VERSION'],
}


class Metric(Enum):
  """List of metric names to avoid clashes."""

  KHALEESI_HEALTH = 1


class AbstractMetric:
  """Basic metric."""

  _metric: MetricWrapperBase
  _id: Metric

  def __init__(
      self, *,
      metric_id: Metric,
      description: str,
      metric_type: Type[MetricWrapperBase],
      additional_labels: List[str],
  ) -> None :
    """Initialize the metric."""
    self._metric = metric_type(
      metric_id.name.lower(),
      description,
      list(server_labels.keys()) + additional_labels,
      registry = REGISTRY,
    )
    self._id = metric_id

  def get_value(self, **kwargs: Any) -> int :
    """Return the current value of the metric."""
    # noinspection PyProtectedMember
    return int(self._metric.labels(**self.labels(**kwargs))._value.get())  # pylint: disable=protected-access

  def labels(self, **kwargs: Any) -> Dict[str, str] :  # pylint: disable=no-self-use
    """Shortcut to get all labels."""
    return { **server_labels, **kwargs }


class GaugeMetric(AbstractMetric):
  """Gauge metric."""

  def __init__(self, *, metric_id: Metric, description: str, additional_labels: List[str]) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metric_id = metric_id,
      description = description,
      metric_type = Gauge,
      additional_labels = additional_labels,
    )

  def set(self, *, gauge_value: int, **kwargs: Any) -> None :
    """Set the metric to the given value."""
    self._metric.labels(**self.labels(**kwargs)).set(gauge_value)


EnumType = TypeVar('EnumType', bound = Enum)  # pylint: disable=invalid-name
class EnumMetric(Generic[EnumType], GaugeMetric):
  """Metric representing enum data."""

  def __init__(self, *, metric_id: Metric, description: str, enum_type: Type[EnumType]) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metric_id = metric_id,
      description = description,
      additional_labels= [ metric_id.name.lower() ],
    )
    for value in enum_type:
      setattr(self, f'set_{value.name.lower()}', partial(self.set, value = value))

  # noinspection PyMethodOverriding
  def set(self, *, value: EnumType) -> None :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ
    """Set the metric to the given value."""
    for enum in type(value):
      super().set(gauge_value = 0, value = enum)
    super().set(gauge_value = 1, value = value)

  def get_value(self, *, value: EnumType) -> int :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,useless-super-delegation
    """Return the current value of the metric."""
    return super().get_value(value = value)

  def labels(self, *, value: EnumType) -> Dict[str, str] :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ
    """Shortcut to get all labels."""
    return super().labels(**{ self._id.name.lower(): value.name.lower() })
