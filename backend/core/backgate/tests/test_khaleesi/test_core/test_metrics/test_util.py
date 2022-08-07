"""Test monitoring metrics utility."""

# Python.
from typing import Generic, Type, Callable, Any

# khaleesi.ninja.
from khaleesi.core.metrics.util import EnumMetric, EnumType, CounterMetric


class EnumMetricTestMixin(Generic[EnumType]):
  """Helper methods for test classes for enum metrics."""

  metric     : EnumMetric[EnumType]
  enum_type  : Type[EnumType]
  subTest    : Callable  # type: ignore[type-arg]
  assertEqual: Callable  # type: ignore[type-arg]

  def test_set(self) -> None :
    """Test setting a value."""
    # Prepare data.
    for value in self.enum_type:
      with self.subTest(value = value.name):
        # Execute test.
        self.metric.set(value = value)
        # Assert result.
        self.assert_enum_metric_value(value = value)

  def assert_enum_metric_value(self, *, value: EnumType) -> None :
    """Assert the metric values."""
    total = 0
    for value_counter in type(value):
      total += self.metric.get_value(value = value_counter)
    self.assertEqual(1, self.metric.get_value(value = value))
    self.assertEqual(1, total)


class CounterMetricTestMixin:
  """Helper methods for test classes for counter metrics with two labels."""

  metric: CounterMetric
  assertEqual: Callable  # type: ignore[type-arg]

  def execute_and_assert_counter(self, *, method: Callable[[], None], **labels: Any) -> None :
    """Execute the increment and assert it worked."""
    # Prepare data.
    original_value = self.metric.get_value(**labels)
    # Execute test.
    method()
    # Assert result.
    new_value = self.metric.get_value(**labels)
    self.assertEqual(original_value + 1, new_value)
