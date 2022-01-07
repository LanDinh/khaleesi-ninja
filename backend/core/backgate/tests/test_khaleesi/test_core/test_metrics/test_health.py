"""Test the server health metric."""

# khaleesi.ninja.
from khaleesi.core.metrics import HEALTH
from khaleesi.core.metrics.health import HealthMetricType
from khaleesi.core.test_util import SimpleTestCase
from tests.test_khaleesi.test_core.test_metrics.test_util import EnumMetricTestHelper


class HealthMetricTestCase(SimpleTestCase, EnumMetricTestHelper):
  """Test the server health metric."""

  def test_set_healthy(self) -> None :
    """Test setting to healthy."""
    # Execute test.
    HEALTH.set_healthy()
    # Assert result.
    self.assert_enum_metric_value(value = HealthMetricType.healthy)

  def test_set_terminating(self) -> None :
    """Test setting to healthy."""
    # Execute test.
    HEALTH.set_terminating()
    # Assert result.
    self.assert_value(value = HealthMetricType.terminating)
