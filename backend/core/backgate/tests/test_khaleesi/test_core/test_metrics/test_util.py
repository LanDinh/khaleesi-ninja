"""Test monitoring metrics utility."""

# Python.
from typing import Generic, Type, Callable, Any

# khaleesi.ninja.
from khaleesi.core.metrics.util import EnumMetric, EnumType, CounterMetric


class EnumMetricTestMixin(Generic[EnumType]):
  """Helper methods for test classes for enum metrics."""

  metric: EnumMetric[EnumType]
  enum_type: Type[EnumType]

  def test_set(self) -> None :
    """Test setting a value."""
    # Prepare data.
    for value in self.enum_type:
      with self.subTest(value = value.name):  # type: ignore[attr-defined]  # pylint: disable=no-member
        # Execute test.
        self.metric.set(value = value)
        # Assert result.
        self.assert_enum_metric_value(value = value)

  def assert_enum_metric_value(self, *, value: EnumType) -> None :
    """Assert the metric values."""
    total = 0
    for value_counter in type(value):
      total += self.metric.get_value(value = value_counter)
    self.assertEqual(1, self.metric.get_value(value = value))  # type: ignore[attr-defined]  # pylint: disable=no-member
    self.assertEqual(1, total)  # type: ignore[attr-defined]  # pylint: disable=no-member


class CounterMetricTestMixin:
  """Helper methods for test classes for counter metrics with two labels."""

  metric: CounterMetric

  def execute_and_assert_counter(self, *, method: Callable[[], None], **labels: Any) -> None :
    """Execute the increment and assert it worked."""
    # Prepare data.
    original_value = self.metric.get_value(**labels)
    # Execute tests.
    method()
    # Assert result.
    new_value = self.metric.get_value(**labels)
    self.assertEqual(original_value + 1, new_value)  # type: ignore[attr-defined]  # pylint: disable=no-member

  def execute_and_assert_in_progress(self, *, method: Callable[[], None], **labels: Any) -> None :
    """Execute the increment and assert it worked."""
    # Prepare data.
    original_value = self.metric.get_in_progress_value(**labels)
    # Execute tests.
    with self.metric.track_in_progress(**labels):
      method()
      # Assert result.
      in_progress_value = self.metric.get_in_progress_value(**labels)
      self.assertEqual(original_value + 1, in_progress_value)  # type: ignore[attr-defined]  # pylint: disable=no-member
    new_value = self.metric.get_in_progress_value(**labels)
    self.assertEqual(original_value, new_value)  # type: ignore[attr-defined]  # pylint: disable=no-member
