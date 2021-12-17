"""Test PrometheusServerInterceptor"""

# Python.
from unittest.mock import MagicMock

# Django.
from django.test import SimpleTestCase

# khaleesi.ninja.
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor


class PrometheusServerInterceptorTest(SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = PrometheusServerInterceptor()

  def test_intercept(self) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    initial_value = self._get_counter_value()
    # Execute test.
    self.interceptor.intercept(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    # Assert result.
    self.assertEqual(initial_value + 1, self._get_counter_value())

  def _get_counter_value(self) -> int :
    return int(self.interceptor._metrics['khaleesi_test_counter']  # pylint: disable=protected-access
      .labels(test_label = 'khaleesi')._value.get())
