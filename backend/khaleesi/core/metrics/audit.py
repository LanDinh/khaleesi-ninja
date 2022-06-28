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
      metric_id         = Metric.KHALEESI_AUDIT_EVENT,
      description       ='Audit event count.',
      additional_labels = [
          'user',
          'grpc_service',
          'grpc_method',
          'target',
          'action_crud_type',
          'action_custom_type',
          'result',
      ],
    )

  def inc(self, *, event: Event) -> None :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
    """Increment the metric."""
    super().inc(**self._get_arguments(event = event))

  def get_value(self, *, event: Event) -> int :  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
    """Increment the metric."""
    return super().get_value(**self._get_arguments(event = event))

  def labels(  # type: ignore[override] # pylint: disable=arguments-renamed,arguments-differ,useless-super-delegation
      self, *,
      user               : 'User.UserType.V',
      action_crud_type   : 'Event.Action.ActionType.V',
      result             : 'Event.Action.ResultType.V',
      **additional_labels: str,
  ) -> Dict[str, str] :
    """Shortcut to get all labels."""
    return super().labels(
      user             = User.UserType.Name(user).lower(),
      action_crud_type = Event.Action.ActionType.Name(action_crud_type).lower(),
      result           = Event.Action.ResultType.Name(result).lower(),
      **additional_labels,
    )

  def _get_arguments(self, *, event: Event) -> Dict[str, Any] :
    """Transform the event into arguments."""
    return {
        'user'              : event.request_metadata.user.type,
        'khaleesi_gate'     : event.request_metadata.caller.khaleesi_gate,
        'khaleesi_service'  : event.request_metadata.caller.khaleesi_service,
        'grpc_service'      : event.request_metadata.caller.grpc_service,
        'grpc_method'       : event.request_metadata.caller.grpc_method,
        'target'            : event.target.type,
        'action_crud_type'  : event.action.crud_type,
        'action_custom_type': event.action.custom_type,
        'result'            : event.action.result,
    }


AUDIT_EVENT = AuditEventMetric()
