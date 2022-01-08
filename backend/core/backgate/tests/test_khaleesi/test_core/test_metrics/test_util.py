"""Test monitoring metrics utility."""

# Python.
from enum import Enum
from typing import TypeVar, Generic, Type, Callable, Tuple, List

# khaleesi.ninja.
from khaleesi.core.metrics.util import EnumMetric


T = TypeVar('T', bound = Enum)  # pylint: disable=invalid-name
class EnumMetricTestMixin(Generic[T]):
  """Helper methods for test classes for enum metrics."""

  metric: EnumMetric[T]
  enum_type: Type[T]
  custom_setters: List[Tuple[T, Callable[[], None]]]

  def test_set(self) -> None :
    """Test setting a value."""
    # Prepare data.
    for value in self.enum_type:
      with self.subTest(value = str(value)):  # type: ignore[attr-defined]  # pylint: disable=no-member
        # Execute test.
        self.metric.set(value = value)
        # Assert result.
        self.assert_enum_metric_value(value = value)

  def test_setters(self) -> None :
    """Test all custom setters."""
    for value, method in self.custom_setters:
      with self.subTest(method = method.__name__):  # type: ignore[attr-defined]  # pylint: disable=no-member
        # Execute test.
        method()
        # Assert result.
        self.assert_enum_metric_value(value = value)

  def assert_enum_metric_value(self, *, value: T) -> None :
    """Assert the metric values."""
    total = 0
    for value_counter in type(value):
      total += self.metric.get_value(value = value_counter)
    self.assertEqual(1, self.metric.get_value(value = value))  # type: ignore[attr-defined]  # pylint: disable=no-member
    self.assertEqual(1, total)  # type: ignore[attr-defined]  # pylint: disable=no-member
