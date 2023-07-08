"""Test the metric initializer."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.metrics.metricInitializer import (
  MetricInitializer as BaseMetricInitializer,
  EventData,
  GrpcData,
)
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User, GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import EventRequest, Event, ServiceCallData


class MetricInitializer(BaseMetricInitializer):
  """Test subclass."""

  def initializeMetrics(self) -> None :
    """Initialize the metrics."""


class BaseMetricInitializerTest(SimpleTestCase):
  """Test the metric initializer."""

  metricInitializer = MetricInitializer(httpRequestId = 'http-request')

  @patch('khaleesi.core.metrics.metricInitializer.addSystemRequestMetadata')
  def testRequests(self, addMetadata: MagicMock) -> None :
    """Test requests."""
    # Prepare data.
    self.metricInitializer.stub = MagicMock()
    # Execute test.
    with patch.object(self.metricInitializer, 'stub') as stub:
      self.metricInitializer.requests()
      # Assert result.
      addMetadata.assert_called_once()
      stub.GetServiceCallData.assert_called_once()

  @patch('khaleesi.core.metrics.metricInitializer.AUDIT_EVENT')
  def testInitializingEvents(self, auditEvent: MagicMock) -> None :
    """Test initializing events metrics."""
    # Prepare data.
    eventData = EventData(
      caller = GrpcData(
        khaleesiGate    = 'khaleesi-gate',
        khaleesiService = 'khaleesi-service',
        grpcService     = 'grpc-service',
        grpcMethod      = 'grpc-method',
      ),
      targetType        = 'target',
      actionCustomTypes = [ 'custom' ]
    )
    events = [ eventData ]
    self.metricInitializer.stub = MagicMock()
    # Execute test.
    self.metricInitializer.initializeMetricsWithData(events = events)
    # Assert result.
    usersCount   = len(User.UserType.items())
    actionsCount = len(Event.Action.ActionType.items()) + 1
    resultsCount = len(Event.Action.ResultType.items())
    self.assertEqual(usersCount * actionsCount * resultsCount, auditEvent.register.call_count)
    arguments     = auditEvent.register.call_args_list
    users         = set()
    crudActions   = set()
    customActions = set()
    results = set()
    for rawArgument in arguments:
      argument: EventRequest = rawArgument.kwargs['event']
      self.assertCaller(
        expected = eventData.caller,
        actual = argument.requestMetadata.grpcCaller,
      )
      users.add(argument.requestMetadata.user.type)
      crudActions.add(argument.event.action.crudType)
      if argument.event.action.customType:
        customActions.add(argument.event.action.customType)
      results.add(argument.event.action.result)
    self.assertEqual(usersCount  , len(users))
    self.assertEqual(actionsCount, len(crudActions) + len(customActions))
    self.assertEqual(resultsCount, len(results))

  @patch('khaleesi.core.metrics.metricInitializer.OUTGOING_REQUESTS')
  @patch('khaleesi.core.metrics.metricInitializer.INCOMING_REQUESTS')
  def testInitializingRequests(
      self,
      incomingRequests: MagicMock,
      outgoingRequests: MagicMock,
  ) -> None :
    """Test initializing request metrics."""
    # Prepare data.
    self.metricInitializer.stub = MagicMock()
    serviceCallData = ServiceCallData()
    callSelf = serviceCallData.callList.add()
    callSelf.call.grpcService = 'grpc-server'
    callSelf.calls.add()
    callOther = serviceCallData.callList.add()
    callOther.call.grpcService = 'some-other-service'
    callOther.calledBy.add()
    self.metricInitializer.stub.GetServiceCallData.return_value = serviceCallData
    # Execute test.
    self.metricInitializer.initializeMetricsWithData(events = [])
    # Assert result.
    incomingRequests.register.assert_called()
    outgoingRequests.register.assert_called()

  def assertCaller(self, *, expected: GrpcData, actual: GrpcCallerDetails) -> None :
    """Assert the caller data is correct."""
    self.assertEqual(expected.khaleesiGate   , actual.khaleesiGate)
    self.assertEqual(expected.khaleesiService, actual.khaleesiService)
    self.assertEqual(expected.grpcService    , actual.grpcService)
    self.assertEqual(expected.grpcMethod     , actual.grpcMethod)
