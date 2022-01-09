"""Monitoring metrics utility."""

# Python.
from enum import Enum
from typing import TypeVar, Generic, Dict, Type, List, Any

# Django.
from django.conf import settings

# Prometheus.
from prometheus_client import Counter, Gauge  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long
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

  KHALEESI_HEALTH            = 1
  KHALEESI_OUTGOING_REQUESTS = 2
  KHALEESI_INCOMING_REQUESTS = 3


class AbstractMetric:
  """Basic metric."""

  _metric: MetricWrapperBase
  _id: Metric

  def __init__(
      self, *,
      metric_id        : Metric,
      description      : str,
      metric_type      : Type[MetricWrapperBase],
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

  def labels(self, **kwargs: str) -> Dict[str, str] :  # pylint: disable=no-self-use
    """Shortcut to get all labels."""
    return {
        **server_labels,
        **{ key: value for key, value in kwargs.items() if not value.startswith('unknown') },
        **{ key: value.upper() for key, value in kwargs.items() if value.startswith('unknown') },
    }

  @staticmethod
  def without_extra_arguments(*, kwargs: Dict[str, Any]) -> Dict[str, Any] :
    """Pass on all arguments except for the self argument."""
    return {
        key: value
        for key, value in kwargs.items()
        if key != 'self' and not key.startswith('__')
    }

class GaugeMetric(AbstractMetric):
  """Gauge metric."""

  _metric: Gauge

  def __init__(self, *, metric_id: Metric, description: str, additional_labels: List[str]) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metric_id         = metric_id,
      description       = description,
      metric_type       = Gauge,
      additional_labels = additional_labels,
    )

  def set(self, *, gauge_value: int, **kwargs: Any) -> None :
    """Set the metric to the given value."""
    self._metric.labels(**self.labels(**kwargs)).set(gauge_value)


class CounterMetric(AbstractMetric):
  """Counter metric."""

  _metric: Counter
  _metric_in_progress: Gauge

  def __init__(self, *, metric_id: Metric, description: str, additional_labels: List[str]) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metric_id         = metric_id,
      description       = description,
      metric_type       = Counter,
      additional_labels = additional_labels,
    )
    self._metric_in_progress = Gauge(
      f'{metric_id.name.lower()}_in_progress',
      description,
      list(server_labels.keys()) + additional_labels,
      registry = REGISTRY,
    )

  def inc(self, **kwargs: Any) -> None :
    """Set the metric to the given value."""
    self._metric.labels(**self.labels(**kwargs)).inc()

  def track_in_progress(self, **kwargs: Any) -> Any :
    """Tracks the number of things in progress."""
    return self._metric_in_progress.labels(**self.labels(**kwargs)).track_inprogress()

  def get_in_progress_value(self, **kwargs: Any) -> int :
    """Return the current value of the metric."""
    # noinspection PyProtectedMember
    return int(self._metric_in_progress.labels(**self.labels(**kwargs))._value.get())  # pylint: disable=protected-access


EnumType = TypeVar('EnumType', bound = Enum)  # pylint: disable=invalid-name
class EnumMetric(Generic[EnumType], GaugeMetric):
  """Metric representing enum data."""

  def __init__(self, *, metric_id: Metric, description: str) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metric_id         = metric_id,
      description       = description,
      additional_labels = [ metric_id.name.lower() ],
    )

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
