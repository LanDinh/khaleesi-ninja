"""Server health metric."""

# Python.
from enum import Enum

# khaleesi.ninja.
from khaleesi.core.metrics.util import EnumMetric, Metric


class HealthMetricType(Enum):
  """Different health states."""

  # pylint: disable=invalid-name

  healthy     = 0
  unhealthy   = 1
  dead        = 2
  terminating = 3


class HealthMetric(EnumMetric[HealthMetricType]):
  """Health metric."""

  def __init__(self) -> None :
    super().__init__(metric_id= Metric.khaleesi_health, description ='Health state.')
    self.set_healthy()

  def set_healthy(self) -> None :
    """Set to healthy."""
    self.set(value = HealthMetricType.healthy)

  def set_terminating(self) -> None :
    """Set to terminating."""
    self.set(value = HealthMetricType.terminating)
