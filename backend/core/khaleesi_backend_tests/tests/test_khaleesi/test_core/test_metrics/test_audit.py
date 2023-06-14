"""Test the audit event metric."""

# Python.
from functools import partial

# khaleesi.ninja.
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
from tests.test_khaleesi.test_core.test_metrics.test_util import CounterMetricTestMixin


class AuditEventMetricTestCase(CounterMetricTestMixin, SimpleTestCase):
  """Test the audit event metric."""

  metric = AUDIT_EVENT

  def test_inc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    for user_label, user_type in User.UserType.items():
      for action_label, action_type in Event.Action.ActionType.items():
        for result_label, result_type in Event.Action.ResultType.items():
          with self.subTest(user = user_label, action = action_label, result = result_label):
            # Prepare data.
            event = self._get_event(
              user = user_type,
              action_crud_type = action_type,
              result = result_type,
            )
            # Execute test & assert result.
            self.execute_and_assert_counter(
              method = partial(self.metric.inc, event = event),
              event = event,
            )

  def _get_event(
      self, *,
      user: 'User.UserType.V',
      action_crud_type: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
  ) -> Event :
    """Construct event."""
    event = Event()
    event.request_metadata.user.type           = user
    event.request_metadata.caller.grpc_service = 'grpc-service'
    event.request_metadata.caller.grpc_method  = 'grpc-method'
    event.target.type = 'target'
    event.action.crud_type   = action_crud_type
    event.action.custom_type = 'action-type'
    event.action.result      = result
    return event
