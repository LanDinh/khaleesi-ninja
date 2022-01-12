"""Test the audit event metric."""

# Python.
from functools import partial

# khaleesi.ninja.
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
from tests.test_khaleesi.test_core.test_metrics.test_util import CounterMetricTestMixin


class AuditEventMetricTestMixin(SimpleTestCase, CounterMetricTestMixin):
  """Test the audit event metric."""

  metric = AUDIT_EVENT
  labels = {
      'grpc_service'      : 'grpc-service',
      'grpc_method'       : 'grpc-method',
      'event'             : 'event',
      'target'            : 'target',
      'action_custom_type': 'action-type',
  }

  def test_inc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    for user_label, user_type in User.UserType.items():
      for action_label, action_type in Event.Action.ActionType.items():
        for result_label, result_type in Event.Action.ResultType.items():
          with self.subTest(user = user_label, action = action_label, result = result_label):
            # Execute test and assert result.
            self.execute_and_assert_counter(
              method = partial(
                self.metric.inc,
                user             = user_type,
                action_crud_type = action_type,
                result           = result_type,
                **self.labels,
              ),
              user             = user_type,
              action_crud_type = action_type,
              result           = result_type,
              **self.labels
            )
