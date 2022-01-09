"""Server requests metrics."""

# Python.
from typing import Dict

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.util import CounterMetric, Metric
from khaleesi.proto.core_pb2 import User


class RequestsMetric(CounterMetric):
  """Health metric."""

  def __init__(self, *, metric_id: Metric) -> None :
    super().__init__(
      metric_id         = metric_id,
      description       ='Request count.',
      additional_labels = [
          'status',
          'user',
          'grpc_service',
          'grpc_method',
          'peer_khaleesi_gate',
          'peer_khaleesi_service',
          'peer_grpc_service',
          'peer_grpc_method',
      ],
    )

  def inc(  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
      self, *,
      status               : StatusCode,
      user                 : int,
      grpc_service         : str,
      grpc_method          : str,
      peer_khaleesi_gate   : str,
      peer_khaleesi_service: str,
      peer_grpc_service    : str,
      peer_grpc_method     : str,
  ) -> None :
    """Increment the metric."""
    super().inc(**self.without_extra_arguments(kwargs = locals()))

  def get_value(  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
      self, *,
      status               : StatusCode,
      user                 : int,
      grpc_service         : str,
      grpc_method          : str,
      peer_khaleesi_gate   : str,
      peer_khaleesi_service: str,
      peer_grpc_service    : str,
      peer_grpc_method     : str,
  ) -> int :
    """Increment the metric."""
    return super().get_value(**self.without_extra_arguments(kwargs = locals()))

  def labels(  # type: ignore[override] # pylint: disable=arguments-renamed,arguments-differ,useless-super-delegation
      self, *,
      status: StatusCode,
      user  : int,
      **additional_labels: str,
  ) -> Dict[str, str] :
    """Shortcut to get all labels."""
    return super().labels(
      status = status.name.lower(),
      user   = User.UserType.Name(user).lower(),
      **additional_labels,
    )


OUTGOING_REQUESTS = RequestsMetric(metric_id = Metric.KHALEESI_OUTGOING_REQUESTS)
INCOMING_REQUESTS = RequestsMetric(metric_id = Metric.KHALEESI_INCOMING_REQUESTS)
