"""Test the server health metric."""

# khaleesi.ninja.
from khaleesi.core.metrics import HEALTH
from khaleesi.core.metrics.health import HealthMetricType
from khaleesi.core.test_util import SimpleTestCase
from tests.test_khaleesi.test_core.test_metrics.test_util import EnumMetricTestMixin


class HealthMetricTestCase(SimpleTestCase, EnumMetricTestMixin[HealthMetricType]):
  """Test the server health metric."""

  metric = HEALTH
  enum_type = HealthMetricType
