"""Test the metric initializer."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
from microservice.metricInitializer import MetricInitializer
from microservice.models.serviceRegistry import (
  KhaleesiGate,
  KhaleesiService,
  GrpcService,
  GrpcMethod,
)


@patch('microservice.metricInitializer.BaseMetricInitializer.initializeMetricsWithData')
@patch('microservice.metricInitializer.SERVICE_REGISTRY')
class MetricInitializerTestCase(SimpleTestCase):
  """Test the metric initializer."""

  def testInit(self, serviceRegistry: MagicMock, *_: MagicMock) -> None :
    """Test initialization."""
    # Prepare data & execute test.
    MetricInitializer(httpRequestId = 'http-request')
    # Assert result.
    serviceRegistry.addService.assert_called_once()

  def testRequests(self, serviceRegistry: MagicMock, *_: MagicMock) -> None :
    """Test the requests are fetched correctly."""
    # Prepare data.
    metricInitializer = MetricInitializer(httpRequestId = 'http-request')
    # Execute test.
    metricInitializer.requests()
    # Assert result.
    serviceRegistry.getCallData.assert_called_once()

  def testInitializeMetrics(
      self,
      serviceRegistry: MagicMock,
      parent: MagicMock,
  ) -> None :
    """Test initialization of metrics."""
    # Prepare data.
    metricInitializer = MetricInitializer(httpRequestId = 'http-request')
    khaleesiGateName    = 'khaleesi-gate'
    khaleesiServiceName = 'khaleesi-service'
    grpcServiceName     = 'grpc-server'
    grpcMethodName      = 'lifecycle'
    serviceRegistry.getServiceRegistry.return_value = {
        khaleesiGateName: KhaleesiGate(
          services = {
              khaleesiServiceName: KhaleesiService(
                services = {
                    grpcServiceName: GrpcService(
                      methods = { grpcMethodName: GrpcMethod() }
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
    end = False
    for event in arguments.kwargs['events']:
      self.assertEqual(khaleesiGateName     , event.caller.khaleesiGate)
      self.assertEqual(khaleesiServiceName  , event.caller.khaleesiService)
      self.assertEqual(grpcServiceName      , event.caller.grpcService)
      self.assertEqual(grpcMethodName       , event.caller.grpcMethod)
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
