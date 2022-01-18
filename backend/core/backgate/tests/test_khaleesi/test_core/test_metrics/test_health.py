"""Test the server health metric."""

# khaleesi.ninja.
from khaleesi.core.metrics.health import HEALTH, HealthMetricType
from khaleesi.core.test_util.test_case import SimpleTestCase
from tests.test_khaleesi.test_core.test_metrics.test_util import EnumMetricTestMixin


class HealthMetricTestCase(EnumMetricTestMixin[HealthMetricType], SimpleTestCase):
  """Test the server health metric."""

  metric = HEALTH
  enum_type = HealthMetricType
