"""Test monitoring metrics utility."""

# Python.
from typing import Generic, Type, Callable, Any

# khaleesi.ninja.
from khaleesi.core.metrics.util import EnumMetric, EnumType, CounterMetric


class EnumMetricTestMixin(Generic[EnumType]):
  """Helper methods for test classes for enum metrics."""

  metric     : EnumMetric[EnumType]
  enumType   : Type[EnumType]
  subTest    : Callable  # type: ignore[type-arg]
  assertEqual: Callable  # type: ignore[type-arg]

  def testSet(self) -> None :
    """Test setting a value."""
    # Prepare data.
    for value in self.enumType:
      with self.subTest(value = value.name):
        # Execute test.
        self.metric.set(value = value)
        # Assert result.
        self.assertEnumMetricValue(value = value)

  def assertEnumMetricValue(self, *, value: EnumType) -> None :
    """Assert the metric values."""
    total = 0
    for valueCounter in type(value):
      total += self.metric.getValue(value = valueCounter)
    self.assertEqual(1, self.metric.getValue(value = value))
    self.assertEqual(1, total)


class CounterMetricTestMixin:
  """Helper methods for test classes for counter metrics with two labels."""

  metric     : CounterMetric
  assertEqual: Callable  # type: ignore[type-arg]

  def executeAndAssertCounter(self, *, method: Callable[[], None], **labels: Any) -> None :
    """Execute the increment and assert it worked."""
    # Prepare data.
    originalValue = self.metric.getValue(**labels)
    # Execute test.
    method()
    # Assert result.
    newValue = self.metric.getValue(**labels)
    self.assertEqual(originalValue + 1, newValue)
