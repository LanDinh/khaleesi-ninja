"""Server audit metrics."""

# Python.
from typing import Dict

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
          'event',
          'target',
          'action_crud_type',
          'action_custom_type',
          'result',
      ],
    )

  def inc(  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
      self, *,
      user              : 'User.UserType.V',
      grpc_service      : str,
      grpc_method       : str,
      event             : str,
      target            : str,
      action_crud_type  : 'Event.Action.ActionType.V',
      action_custom_type: str,
      result            : 'Event.Action.ResultType.V',
  ) -> None :
    """Increment the metric."""
    super().inc(**self.without_extra_arguments(kwargs = locals()))

  def get_value(  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
      self, *,
      user              : 'User.UserType.V',
      grpc_service      : str,
      grpc_method       : str,
      event             : str,
      target            : str,
      action_crud_type  : 'Event.Action.ActionType.V',
      action_custom_type: str,
      result       : 'Event.Action.ResultType.V',
  ) -> int :
    """Increment the metric."""
    return super().get_value(**self.without_extra_arguments(kwargs = locals()))

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


AUDIT_EVENT = AuditEventMetric()
