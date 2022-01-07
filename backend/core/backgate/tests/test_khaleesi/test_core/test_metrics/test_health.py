"""Test the server health metric."""

# khaleesi.ninja.
from khaleesi.core.metrics import HEALTH
from khaleesi.core.metrics.health import HealthMetricType
from khaleesi.core.test_util import SimpleTestCase


class HealthMetricTestCase(SimpleTestCase):
  """Test the server health metric."""

  def test_set_healthy(self) -> None :
    """Test setting to healthy."""
    # Execute test.
    HEALTH.set_healthy()
    # Assert result.
    self.assert_value(value = HealthMetricType.healthy)

  def test_set_terminating(self) -> None :
    """Test setting to healthy."""
    # Execute test.
    HEALTH.set_terminating()
    # Assert result.
    self.assert_value(value = HealthMetricType.terminating)

  def assert_value(self, *, value: HealthMetricType) -> None :
    """Assert the metric value."""
    total = 0
    for value_counter in HealthMetricType:
      total += HEALTH.get_value(value = value_counter)
    self.assertEqual(1, HEALTH.get_value(value = value))
    self.assertEqual(1, total)
