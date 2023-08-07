"""Test the metric initializer."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
from microservice.metricInitializer import MetricInitializer
from microservice.models.siteRegistry import (
  Site,
  App,
  Service,
  Method,
)


@patch('microservice.metricInitializer.BaseMetricInitializer.initializeMetricsWithData')
@patch('microservice.metricInitializer.SITE_REGISTRY')
class MetricInitializerTestCase(SimpleTestCase):
  """Test the metric initializer."""

  def testInit(self, siteRegistry: MagicMock, *_: MagicMock) -> None :
    """Test initialization."""
    # Prepare data & execute test.
    MetricInitializer(httpRequestId = 'http-request')
    # Assert result.
    siteRegistry.addService.assert_called_once()

  def testRequests(self, siteRegistry: MagicMock, *_: MagicMock) -> None :
    """Test the requests are fetched correctly."""
    # Prepare data.
    metricInitializer = MetricInitializer(httpRequestId = 'http-request')
    # Execute test.
    metricInitializer.requests()
    # Assert result.
    siteRegistry.getCallData.assert_called_once()

  def testInitializeMetrics(
      self,
      siteRegistry: MagicMock,
      parent: MagicMock,
  ) -> None :
    """Test initialization of metrics."""
    # Prepare data.
    metricInitializer = MetricInitializer(httpRequestId = 'http-request')
    siteName    = 'site'
    appName     = 'app'
    serviceName = 'grpc-server'
    methodName  = 'lifecycle'
    siteRegistry.getSiteRegistry.return_value = {
        siteName: Site(
          apps = {
              appName: App(
                services = {
                    serviceName: Service(
                      methods = { methodName: Method() }
                    )
                }
              )
          }
        )
    }
    # Execute test.
    metricInitializer.initializeMetrics()
    # Assert result.
    parent.assert_called_once()
    arguments = parent.call_args
    start = False
    end  = False
    for event in arguments.kwargs['events']:
      self.assertEqual(siteName   , event.caller.site)
      self.assertEqual(appName    , event.caller.app)
      self.assertEqual(serviceName, event.caller.service)
      self.assertEqual(methodName , event.caller.method)
      self.assertEqual('core.core.server'   , event.targetType)
      self.assertEqual(1                    , len(event.userTypes))
      self.assertEqual(User.UserType.SYSTEM , event.userTypes[0])
      self.assertEqual(1                    , len(event.actionCrudTypes))
      if event.actionCrudTypes[0] == Event.Action.ActionType.START:
        start = True
      if event.actionCrudTypes[0] == Event.Action.ActionType.END:
        end = True
    self.assertTrue(start)
    self.assertTrue(end)
