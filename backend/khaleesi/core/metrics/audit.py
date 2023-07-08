"""Server audit metrics."""

# Python.
from typing import Dict, Any

# khaleesi.ninja.
from khaleesi.core.metrics.util import CounterMetric, Metric
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import EventRequest, Event


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

  def inc(self, *, event: EventRequest) -> None :  # type: ignore[override]  # pylint: disable=arguments-differ
    """Increment the metric."""
    super().inc(**self._getArguments(event = event))

  def register(self, *, event: EventRequest) -> None :  # type: ignore[override]  # pylint: disable=arguments-differ
    """Increment the metric."""
    super().register(**self._getArguments(event = event))  # pragma: no cover

  def getValue(self, *, event: EventRequest) -> int :  # type: ignore[override]  # pylint: disable=arguments-differ
    """Increment the metric."""
    return super().getValue(**self._getArguments(event = event))

  def labels(  # type: ignore[override] # pylint: disable=arguments-differ,useless-super-delegation
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

  def _getArguments(self, *, event: EventRequest) -> Dict[str, Any] :
    """Transform the event into arguments."""
    return {
        'user'            : event.requestMetadata.user.type,
        'khaleesiGate'    : event.requestMetadata.grpcCaller.khaleesiGate,
        'khaleesiService' : event.requestMetadata.grpcCaller.khaleesiService,
        'grpcService'     : event.requestMetadata.grpcCaller.grpcService,
        'grpcMethod'      : event.requestMetadata.grpcCaller.grpcMethod,
        'target'          : event.event.target.type,
        'actionCrudType'  : event.event.action.crudType,
        'actionCustomType': event.event.action.customType,
        'result'          : event.event.action.result,
    }


AUDIT_EVENT = AuditEventMetric()
