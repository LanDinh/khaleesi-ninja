"""Monitoring metrics utility."""

# Python.
from enum import Enum
from typing import TypeVar, Generic, Dict

# Django.
from django.conf import settings

# Prometheus.
from prometheus_client import Gauge  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long
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


T = TypeVar('T', bound = Enum)  # pylint: disable=invalid-name


class EnumMetric(Generic[T]):
  """Metric representing enum data."""

  _metric: Gauge
  _id: Metric

  def __init__(self, *, metric_id: Metric, description: str) -> None :
    """Initialize the enum metric."""
    self._metric = Gauge(
      metric_id.name.lower(),
      description,
      list(server_labels.keys()) + [ metric_id.name.lower() ],
      registry = REGISTRY,
    )
    self._id = metric_id

  def set(self, *, value: T) -> None :
    """Set the metric to the given value."""
    for enum in type(value):
      self._metric.labels(**self._labels(value = enum)).set(0)
    self._metric.labels(**self._labels(value = value)).set(1)

  def get_value(self, *, value: T) -> int :
    """Return the current value of the metric."""
    # noinspection PyProtectedMember
    return int(self._metric.labels(**self._labels(value = value))._value.get())  # pylint: disable=protected-access

  def _labels(self, *, value: T) -> Dict[str, str] :
    """Shortcut to get all labels."""
    return { **server_labels, self._id.name.lower(): value.name.lower() }
