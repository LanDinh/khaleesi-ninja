"""Server requests metrics."""

# Python.
from typing import Dict, Any

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.util import CounterMetric, Metric
from khaleesi.proto.core_pb2 import User, RequestMetadata


class RequestsMetric(CounterMetric):
  """Request metric."""

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
      request: RequestMetadata,
      peer   : RequestMetadata,
      status : StatusCode,
  ) -> None :
    """Increment the metric."""
    super().inc(status = status, **self._get_arguments(request = request, peer = peer))

  def get_value(  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
      self, *,
      request: RequestMetadata,
      peer   : RequestMetadata,
      status : StatusCode,
  ) -> int :
    """Increment the metric."""
    return super().get_value(status = status, **self._get_arguments(request = request, peer = peer))

  def labels(  # type: ignore[override] # pylint: disable=arguments-renamed,arguments-differ,useless-super-delegation
      self, *,
      status             : StatusCode,
      user               : 'User.UserType.V',
      **additional_labels: str,
  ) -> Dict[str, str] :
    """Shortcut to get all labels."""
    return super().labels(
      status = status.name.lower(),
      user   = User.UserType.Name(user).lower(),
      **additional_labels,
    )

  def _get_arguments(
      self, *,
      request: RequestMetadata,
      peer   : RequestMetadata,
  ) -> Dict[str, Any] :
    """Transform the request metadata into arguments."""
    return {
        'user': request.user.type,
        'grpc_service': self.string_or_unknown(request.caller.grpc_service),
        'grpc_method' : self.string_or_unknown(request.caller.grpc_method),
        'peer_khaleesi_gate'   : self.string_or_unknown(peer.caller.khaleesi_gate),
        'peer_khaleesi_service': self.string_or_unknown(peer.caller.khaleesi_service),
        'peer_grpc_service'    : self.string_or_unknown(peer.caller.grpc_service),
        'peer_grpc_method'     : self.string_or_unknown(peer.caller.grpc_method),
    }


OUTGOING_REQUESTS = RequestsMetric(metric_id = Metric.KHALEESI_OUTGOING_REQUESTS)
INCOMING_REQUESTS = RequestsMetric(metric_id = Metric.KHALEESI_INCOMING_REQUESTS)
