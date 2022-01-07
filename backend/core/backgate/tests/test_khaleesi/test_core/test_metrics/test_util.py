"""Test monitoring metrics utility."""

# Python.
from enum import Enum
from typing import TypeVar, Generic

# khaleesi.ninja.
from khaleesi.core.metrics import HEALTH
from khaleesi.core.metrics.health import HealthMetricType
from khaleesi.core.metrics.util import EnumMetric
from khaleesi.core.test_util import SimpleTestCase


T = TypeVar('T', bound = Enum)  # pylint: disable=invalid-name


class EnumMetricTestMixin(Generic[T]):
  """Helper methods for test classes for enum metrics."""

  metric: EnumMetric[T]

  def assert_enum_metric_value(self, *, value: T) -> None :
    """Assert the metric values."""
    total = 0
    for value_counter in type(value):
      total += self.metric.get_value(value = value_counter)
    self.assertEqual(1, self.metric.get_value(value = value))  # type: ignore[attr-defined]  # pylint: disable=no-member
    self.assertEqual(1, total)  # type: ignore[attr-defined]  # pylint: disable=no-member


class EnumMetricTestCase(SimpleTestCase, EnumMetricTestMixin[HealthMetricType]):
  """Test metric representing enum data."""

  metric = HEALTH

  def test_set(self) -> None :
    """Test setting a value."""
    # Prepare data.
    for value in HealthMetricType:
      with self.subTest(value = str(value)):
        # Execute test.
        HEALTH.set(value = value)
        # Assert result.
        self.assert_enum_metric_value(value = value)
