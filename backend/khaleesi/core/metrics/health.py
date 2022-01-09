"""Server health metric."""

# Python.
from enum import Enum

# khaleesi.ninja.
from typing import Callable

from khaleesi.core.metrics.util import EnumMetric, Metric


class HealthMetricType(Enum):
  """Different health states."""

  HEALTHY     = 0
  UNHEALTHY   = 1
  DEAD        = 2
  TERMINATING = 3


class HealthMetric(EnumMetric[HealthMetricType]):
  """Health metric."""

  set_healthy    : Callable[[], None]
  set_terminating: Callable[[], None]

  def __init__(self) -> None :
    super().__init__(
      metric_id= Metric.KHALEESI_HEALTH,
      description ='Health state.',
      enum_type = HealthMetricType,
    )
    self.set_healthy()


HEALTH = HealthMetric()
