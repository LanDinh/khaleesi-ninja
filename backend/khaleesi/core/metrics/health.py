"""Server health metric."""

# Python.
from enum import Enum

# khaleesi.ninja.
from khaleesi.core.metrics.util import EnumMetric, Metric


class HealthMetricType(Enum):
  """Different health states."""

  HEALTHY     = 0
  UNHEALTHY   = 1
  DEAD        = 2
  TERMINATING = 3


class HealthMetric(EnumMetric[HealthMetricType]):
  """Health metric."""

  def __init__(self) -> None :
    super().__init__(metric_id= Metric.KHALEESI_HEALTH, description ='Health state.')
    self.set(value = HealthMetricType.HEALTHY)


HEALTH = HealthMetric()
