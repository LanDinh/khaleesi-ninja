"""Server audit metrics."""

# Python.
from typing import Dict, Any

# khaleesi.ninja.
from khaleesi.core.metrics.util import CounterMetric, Metric
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event


class AuditEventMetric(CounterMetric):
  """Health metric."""

  def __init__(self) -> None :
    super().__init__(
      metricId         = Metric.KHALEESI_AUDIT_EVENT,
      description      ='Audit event count.',
      additionalLabels = [
          'user',
          'grpcService',
          'grpcMethod',
          'target',
          'actionCrudType',
          'actionCustomType',
          'result',
      ],
    )

  def inc(self, *, event: Event) -> None :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
    """Increment the metric."""
    super().inc(**self._getArguments(event = event))

  def register(self, *, event: Event) -> None :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
    """Increment the metric."""
    super().register(**self._getArguments(event = event))  # pragma: no cover

  def getValue(self, *, event: Event) -> int :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
    """Increment the metric."""
    return super().getValue(**self._getArguments(event = event))

  def labels(  # type: ignore[override] # pylint: disable=arguments-renamed,arguments-differ,useless-super-delegation
      self, *,
      user              : 'User.UserType.V',
      actionCrudType    : 'Event.Action.ActionType.V',
      result            : 'Event.Action.ResultType.V',
      **additionalLabels: str,
  ) -> Dict[str, str] :
    """Shortcut to get all labels."""
    return super().labels(
      user           = User.UserType.Name(user).lower(),
      actionCrudType = Event.Action.ActionType.Name(actionCrudType).lower(),
      result         = Event.Action.ResultType.Name(result).lower(),
      **additionalLabels,
    )

  def _getArguments(self, *, event: Event) -> Dict[str, Any] :
    """Transform the event into arguments."""
    return {
        'user'            : event.requestMetadata.user.type,
        'khaleesiGate'    : event.requestMetadata.caller.khaleesiGate,
        'khaleesiService' : event.requestMetadata.caller.khaleesiService,
        'grpcService'     : event.requestMetadata.caller.grpcService,
        'grpcMethod'      : event.requestMetadata.caller.grpcMethod,
        'target'          : event.target.type,
        'actionCrudType'  : event.action.crudType,
        'actionCustomType': event.action.customType,
        'result'          : event.action.result,
    }


AUDIT_EVENT = AuditEventMetric()
