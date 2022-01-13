"""Server requests metrics."""

# Python.
from typing import Dict, Any

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.util import CounterMetric, Metric
from khaleesi.proto.core_pb2 import User, RequestMetadata


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
      request_metadata : RequestMetadata,
      status           : StatusCode,
      grpc_service     : str,
      grpc_method      : str,
  ) -> None :
    """Increment the metric."""
    super().inc(
      status           = status,
      grpc_service     = grpc_service,
      grpc_method      = grpc_method,
      **self._get_arguments(request_metadata = request_metadata),
    )

  def get_value(  # type: ignore[override]  # pylint: disable=arguments-renamed,arguments-differ,unused-argument
      self, *,
      request_metadata : RequestMetadata,
      status           : StatusCode,
      grpc_service     : str,
      grpc_method      : str,
  ) -> int :
    """Increment the metric."""
    return super().get_value(
      status           = status,
      grpc_service     = grpc_service,
      grpc_method      = grpc_method,
      **self._get_arguments(request_metadata = request_metadata),
    )

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

  @staticmethod
  def string_or_unknown(value: str) -> str :
    """Either return the value, or UNKNOWN if empty."""
    if value:
      return value
    return 'UNKNOWN'

  def _get_arguments(
      self, *,
      request_metadata: RequestMetadata,
  ) -> Dict[str, Any] :
    """Transform the request metadata into arguments."""
    return {
        'peer_khaleesi_gate'   : self.string_or_unknown(request_metadata.caller.khaleesi_gate),
        'peer_khaleesi_service': self.string_or_unknown(request_metadata.caller.khaleesi_service),
        'peer_grpc_service'    : self.string_or_unknown(request_metadata.caller.grpc_service),
        'peer_grpc_method'     : self.string_or_unknown(request_metadata.caller.grpc_method),
        'user'                 : request_metadata.user.type,
    }


OUTGOING_REQUESTS = RequestsMetric(metric_id = Metric.KHALEESI_OUTGOING_REQUESTS)
INCOMING_REQUESTS = RequestsMetric(metric_id = Metric.KHALEESI_INCOMING_REQUESTS)
