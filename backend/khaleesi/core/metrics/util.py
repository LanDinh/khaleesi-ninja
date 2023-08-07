"""Monitoring metrics utility."""

# Python.
from enum import Enum
from typing import TypeVar, Generic, Dict, Type, List, Any

# Django.
from django.conf import settings

# Prometheus.
from prometheus_client import Counter, Gauge
from prometheus_client.metrics import MetricWrapperBase
from prometheus_client.registry import REGISTRY

# khaleesi.ninja.
from khaleesi.core.settings.definition import Metadata


khaleesiSettings: Metadata = settings.KHALEESI_NINJA['METADATA']
serverLabels = {
    'site'           : khaleesiSettings['SITE'],
    'app'            : khaleesiSettings['APP'],
    'khaleesiType'   : khaleesiSettings['TYPE'].name.lower(),
    'khaleesiVersion': khaleesiSettings['VERSION'],
}


class Metric(Enum):
  """List of metric names to avoid clashes."""

  KHALEESI_HEALTH            = 1
  KHALEESI_OUTGOING_REQUESTS = 2
  KHALEESI_INCOMING_REQUESTS = 3
  KHALEESI_AUDIT_EVENT       = 4


class AbstractMetric:
  """Basic metric."""

  _metric: MetricWrapperBase
  _id    : Metric

  def __init__(
      self, *,
      metricId        : Metric,
      description     : str,
      metricType      : Type[MetricWrapperBase],
      additionalLabels: List[str],
  ) -> None :
    """Initialize the metric."""
    self._metric = metricType(
      metricId.name.lower(),
      description,
      list(serverLabels.keys()) + additionalLabels,
      registry = REGISTRY,
    )
    self._id = metricId

  def getValue(self, **kwargs: Any) -> int :
    """Return the current value of the metric."""
    # noinspection PyProtectedMember
    return int(self._metric.labels(**self.labels(**kwargs))._value.get())  # type: ignore[attr-defined]  # pylint: disable=protected-access

  def labels(self, **kwargs: str) -> Dict[str, str] :
    """Shortcut to get all labels."""
    return {
        **serverLabels,
        **{ key: value for key, value in kwargs.items() if not value.startswith('unknown') },
        **{ key: value.upper() for key, value in kwargs.items() if value.startswith('unknown') },
    }

  def stringOrUnknown(self, value: str) -> str :
    """Either return the value, or UNKNOWN if empty."""
    if value:
      return value
    return 'UNKNOWN'

class GaugeMetric(AbstractMetric):
  """Gauge metric."""

  _metric: Gauge

  def __init__(self, *, metricId: Metric, description: str, additionalLabels: List[str]) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metricId         = metricId,
      description      = description,
      metricType       = Gauge,
      additionalLabels = additionalLabels,
    )

  def set(self, *, gaugeValue: int, **kwargs: Any) -> None :
    """Set the metric to the given value."""
    self._metric.labels(**self.labels(**kwargs)).set(gaugeValue)


class CounterMetric(AbstractMetric):
  """Counter metric."""

  _metric: Counter

  def __init__(self, *, metricId: Metric, description: str, additionalLabels: List[str]) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metricId         = metricId,
      description      = description,
      metricType       = Counter,
      additionalLabels = additionalLabels,
    )

  def inc(self, **kwargs: Any) -> None :
    """Set the metric to the given value."""
    self._metric.labels(**self.labels(**kwargs)).inc()

  def register(self, **kwargs: Any) -> None :
    """Set the metric to the given value."""
    self._metric.labels(**self.labels(**kwargs))  # pragma: no cover


EnumType = TypeVar('EnumType', bound = Enum)  # pylint: disable=invalid-name
class EnumMetric(Generic[EnumType], GaugeMetric):
  """Metric representing enum data."""

  def __init__(self, *, metricId: Metric, description: str) -> None :
    """Initialize the enum metric."""
    super().__init__(
      metricId         = metricId,
      description      = description,
      additionalLabels = [ metricId.name.lower() ],
    )

  # noinspection PyMethodOverriding
  def set(self, *, value: EnumType) -> None :  # type: ignore[override]  # pylint: disable=arguments-differ
    """Set the metric to the given value."""
    for enum in type(value):
      super().set(gaugeValue = 0, value = enum)
    super().set(gaugeValue = 1, value = value)

  def getValue(self, *, value: EnumType) -> int :  # type: ignore[override]  # pylint: disable=arguments-differ,useless-super-delegation
    """Return the current value of the metric."""
    return super().getValue(value = value)

  def labels(self, *, value: EnumType) -> Dict[str, str] :  # type: ignore[override]  # pylint: disable=arguments-differ
    """Shortcut to get all labels."""
    return super().labels(**{ self._id.name.lower(): value.name.lower() })
