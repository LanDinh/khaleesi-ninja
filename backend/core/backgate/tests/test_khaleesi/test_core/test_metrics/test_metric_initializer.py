"""Test the metric initializer."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.metrics.metric_initializer import BaseMetricInitializer, EventData, GrpcData
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User, GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import Event


class BaseMetricInitializerTest(SimpleTestCase):
  """Test the metric initializer."""

  metric_initializer = BaseMetricInitializer(channel_manager = MagicMock())

  def test_force_initialization_method(self) -> None :
    """Test all subclasses need to override the base method."""
    # Execute test & assert result.
    with self.assertRaises(ProgrammingException):
      self.metric_initializer.initialize_metrics()

  @patch('khaleesi.core.metrics.metric_initializer.add_grpc_server_system_request_metadata')
  def test_requests(self, add_metadata: MagicMock) -> None :
    """Test requests."""
    # Execute test.
    with patch.object(self.metric_initializer, 'stub') as stub:
      self.metric_initializer.requests()
      # Assert result.
      add_metadata.assert_called_once()
      stub.GetServiceCallData.assert_called_once()

  @patch('khaleesi.core.metrics.metric_initializer.AUDIT_EVENT')
  def test_initializing_events(self, audit_event: MagicMock) -> None :
    """Test initializing events metrics."""
    # Prepare data.
    event_data = EventData(
      caller = GrpcData(
        khaleesi_gate = 'khaleesi-gate',
        khaleesi_service = 'khaleesi-service',
        grpc_service = 'grpc-service',
        grpc_method = 'grpc-method',
      ),
      target_type = 'target',
      action_custom_types = [ 'custom' ]
    )
    events = [ event_data ]
    # Execute test.
    self.metric_initializer.initialize_metrics_with_data(events = events)
    # Assert result.
    users_count = len(User.UserType.items())
    actions_count = len(Event.Action.ActionType.items()) + 1
    results_count = len(Event.Action.ResultType.items())
    self.assertEqual(users_count * actions_count * results_count, audit_event.register.call_count)
    arguments = audit_event.register.call_args_list
    users   = set()
    crud_actions = set()
    custom_actions = set()
    results = set()
    for raw_argument in arguments:
      argument: Event = raw_argument.kwargs['event']
      self.assert_caller(expected = event_data.caller, actual = argument.request_metadata.caller)
      users.add(argument.request_metadata.user.type)
      crud_actions.add(argument.action.crud_type)
      if argument.action.custom_type:
        custom_actions.add(argument.action.custom_type)
      results.add(argument.action.result)
    self.assertEqual(users_count  , len(users))
    self.assertEqual(actions_count, len(crud_actions) + len(custom_actions))
    self.assertEqual(results_count, len(results))

  @patch('khaleesi.core.metrics.metric_initializer.OUTGOING_REQUESTS')
  @patch('khaleesi.core.metrics.metric_initializer.INCOMING_REQUESTS')
  def test_initializing_requests(
      self,
      incoming_requests: MagicMock,
      outgoing_requests: MagicMock,
  ) -> None :
    """Test initializing request metrics."""
    # Execute test.
    self.metric_initializer.initialize_metrics_with_data(events = [])
    # Assert result.
    incoming_arguments = incoming_requests.register.call_args_list
    outgoing_arguments = outgoing_requests.register.call_args_list
    self.assertEqual(0  , len(incoming_arguments))
    self.assertEqual(0, len(outgoing_arguments))

  def assert_caller(self, *, expected: GrpcData, actual: GrpcCallerDetails) -> None :
    """Assert the caller data is correct."""
    self.assertEqual(expected.khaleesi_gate   , actual.khaleesi_gate)
    self.assertEqual(expected.khaleesi_service, actual.khaleesi_service)
    self.assertEqual(expected.grpc_service    , actual.grpc_service)
    self.assertEqual(expected.grpc_method     , actual.grpc_method)
