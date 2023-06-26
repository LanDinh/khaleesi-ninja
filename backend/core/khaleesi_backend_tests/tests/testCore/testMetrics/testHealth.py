"""Test the server health metric."""

# khaleesi.ninja.
from khaleesi.core.metrics.health import HEALTH, HealthMetricType
from khaleesi.core.testUtil.testCase import SimpleTestCase
from tests.testCore.testMetrics.testUtil import EnumMetricTestMixin


class HealthMetricTestCase(EnumMetricTestMixin[HealthMetricType], SimpleTestCase):
  """Test the server health metric."""

  metric   = HEALTH
  enumType = HealthMetricType
