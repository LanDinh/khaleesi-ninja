"""Test monitoring metrics utility."""

# Python.
from enum import Enum

# khaleesi.ninja.
from khaleesi.core.metrics import HEALTH
from khaleesi.core.metrics.health import HealthMetricType
from khaleesi.core.test_util import SimpleTestCase


class EnumMetricTestCase(SimpleTestCase):
  """Test metric representing enum data."""

  def test_set(self) -> None :
    """Test setting a value."""
    # Prepare data.
    for value in HealthMetricType:
      with self.subTest(value = str(value)):
        # Execute test.
        HEALTH.set(value = value)
        # Assert result.
        total = 0
        for value_counter in HealthMetricType:
          total += HEALTH.get_value(value = value_counter)
        self.assertEqual(1, HEALTH.get_value(value = value))
        self.assertEqual(1, total)
