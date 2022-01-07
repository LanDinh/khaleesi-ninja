"""Test monitoring metrics utility."""

# Python.
from enum import Enum
from typing import TypeVar, Callable

# khaleesi.ninja.
from khaleesi.core.metrics import HEALTH
from khaleesi.core.metrics.health import HealthMetricType
from khaleesi.core.test_util import SimpleTestCase


T = TypeVar('T', bound = Enum)  # pylint: disable=invalid-name


class EnumMetricTestHelper:
  """Helper methods for test classes for enum metrics."""

  assertEqual: Callable[ [int, int], None ]

  def assert_enum_metric_value(self, *, value: T):
    """Assert the metric values."""
    total = 0
    for value_counter in type(value):
      total += HEALTH.get_value(value = value_counter)
    self.assertEqual(1, HEALTH.get_value(value = value))
    self.assertEqual(1, total)


class EnumMetricTestCase(SimpleTestCase, EnumMetricTestHelper):
  """Test metric representing enum data."""

  def test_set(self) -> None :
    """Test setting a value."""
    # Prepare data.
    for value in HealthMetricType:
      with self.subTest(value = str(value)):
        # Execute test.
        HEALTH.set(value = value)
        # Assert result.
        self.assert_enum_metric_value(value = value)
