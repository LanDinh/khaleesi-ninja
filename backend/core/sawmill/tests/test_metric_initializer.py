"""Test the metric initializer."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from metric_initializer import MetricInitializer


@patch('metric_initializer.SERVICE_REGISTRY')
class MetricInitializerTestCase(SimpleTestCase):
  """Test the metric initializer."""

  def test_init(self, service_registry: MagicMock) -> None :
    """Test initialization."""
    # Prepare data & execute test.
    MetricInitializer()
    # Assert result.
    service_registry.reload.assert_called_once_with()
