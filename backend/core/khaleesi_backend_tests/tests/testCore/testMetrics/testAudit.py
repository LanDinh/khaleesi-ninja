"""Test the audit event metric."""

# Python.
from functools import partial

# khaleesi.ninja.
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event, EventRequest
from tests.testCore.testMetrics.testUtil import CounterMetricTestMixin


class AuditEventMetricTestCase(CounterMetricTestMixin, SimpleTestCase):
  """Test the audit event metric."""

  metric = AUDIT_EVENT

  def testInc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    for userLabel, userType in User.UserType.items():
      for actionLabel, actionType in Event.Action.ActionType.items():
        for resultLabel, resultType in Event.Action.ResultType.items():
          with self.subTest(user = userLabel, action = actionLabel, result = resultLabel):
            # Prepare data.
            event = self._getEvent(
              user           = userType,
              actionCrudType = actionType,
              result         = resultType,
            )
            # Execute test & assert result.
            self.executeAndAssertCounter(
              method = partial(self.metric.inc, event = event),
              event  = event,
            )

  def _getEvent(
      self, *,
      user          : 'User.UserType.V',
      actionCrudType: 'Event.Action.ActionType.V',
      result        : 'Event.Action.ResultType.V',
  ) -> EventRequest :
    """Construct event."""
    event = EventRequest()
    event.requestMetadata.user.type = user
    event.requestMetadata.grpcCaller.service = 'service'
    event.requestMetadata.grpcCaller.method  = 'method'
    event.event.target.type = 'target'
    event.event.action.crudType   = actionCrudType
    event.event.action.customType = 'action-type'
    event.event.action.result     = result
    return event
