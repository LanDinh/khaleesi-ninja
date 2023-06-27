"""Test the metric initializer."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from microservice.metricInitializer import MetricInitializer
from khaleesi.core.testUtil.testCase import SimpleTestCase


class MetricInitializerTest(SimpleTestCase):
  """Test the metric initializer."""

  metricInitializer = MetricInitializer(httpRequestId = 'http-request')

  @patch("microservice.metricInitializer.BaseMetricInitializer.initializeMetricsWithData")
  def testInitializeMetrics(self, superCall: MagicMock) -> None :
    """Test initializing metrics."""
    # Execute tests.
    self.metricInitializer.initializeMetrics()
    # Assert result.
    superCall.assert_called_once()
