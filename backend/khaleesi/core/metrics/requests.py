"""Server requests metrics."""

# Python.
from typing import Dict, Any

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.util import CounterMetric, Metric
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.proto.core_pb2 import User, RequestMetadata


class RequestsMetric(CounterMetric):
  """Request metric."""

  def __init__(self, *, metricId: Metric) -> None :
    super().__init__(
      metricId         = metricId,
      description      ='Request count.',
      additionalLabels = [
          'status',
          'user',
          'grpcService',
          'grpcMethod',
          'peerKhaleesiGate',
          'peerKhaleesiService',
          'peerGrpcService',
          'peerGrpcMethod',
      ],
    )

  def inc(  # type: ignore[override]  # pylint: disable=arguments-differ
      self, *,
      request: RequestMetadata,
      peer   : RequestMetadata,
      status : StatusCode,
  ) -> None :
    """Increment the metric."""
    super().inc(status = status, **self._getArguments(request = request, peer = peer))

  def register(  # type: ignore[override]  # pylint: disable=arguments-differ
      self, *,
      request: RequestMetadata,
      peer   : RequestMetadata,
      status : StatusCode,
  ) -> None :
    """Increment the metric."""
    super().register(status = status, **self._getArguments(request = request, peer = peer))  # pragma: no cover  # pylint: disable=line-too-long

  def getValue(  # type: ignore[override]  # pylint: disable=arguments-differ
      self, *,
      request: RequestMetadata,
      peer   : RequestMetadata,
      status : StatusCode,
  ) -> int :
    """Increment the metric."""
    return super().getValue(status = status, **self._getArguments(request = request, peer = peer))

  def labels(  # type: ignore[override] # pylint: disable=arguments-differ,useless-super-delegation
      self, *,
      status            : StatusCode,
      user              : 'User.UserType.V',
      **additionalLabels: str,
  ) -> Dict[str, str] :
    """Shortcut to get all labels."""
    return super().labels(
      status = self._mapGrpcStatus(status = status),
      user   = User.UserType.Name(user).lower(),
      **additionalLabels,
    )

  def _getArguments(
      self, *,
      request: RequestMetadata,
      peer   : RequestMetadata,
  ) -> Dict[str, Any] :
    """Transform the request metadata into arguments."""
    return {
        'user'               : request.user.type,
        'grpcService'        : self.stringOrUnknown(request.grpcCaller.grpcService),
        'grpcMethod'         : self.stringOrUnknown(request.grpcCaller.grpcMethod),
        'peerKhaleesiGate'   : self.stringOrUnknown(peer.grpcCaller.khaleesiGate),
        'peerKhaleesiService': self.stringOrUnknown(peer.grpcCaller.khaleesiService),
        'peerGrpcService'    : self.stringOrUnknown(peer.grpcCaller.grpcService),
        'peerGrpcMethod'     : self.stringOrUnknown(peer.grpcCaller.grpcMethod),
    }

  def _mapGrpcStatus(self, *, status: StatusCode) -> str :
    """Group status codes."""
    if status == StatusCode.OK:
      return 'ok'
    if status in [
        StatusCode.INVALID_ARGUMENT,
        StatusCode.UNAUTHENTICATED,
        StatusCode.PERMISSION_DENIED,
        StatusCode.NOT_FOUND,
    ]:
      return 'client error'
    if status in [ StatusCode.INTERNAL, StatusCode.UNIMPLEMENTED ]:
      return 'server error'
    if status in [
        StatusCode.CANCELLED,
        StatusCode.DEADLINE_EXCEEDED,
        StatusCode.RESOURCE_EXHAUSTED,
        StatusCode.UNAVAILABLE,
    ]:
      return 'not finished'
    if status in [  # not used by the library nor by khaleesi.ninja.
        StatusCode.UNKNOWN,
        StatusCode.ALREADY_EXISTS,
        StatusCode.FAILED_PRECONDITION,
        StatusCode.ABORTED,
        StatusCode.OUT_OF_RANGE,
        StatusCode.DATA_LOSS,
    ]:
      return 'unknown'

    raise ProgrammingException(  # pragma: no cover
      privateMessage = 'Unknown gRPC status returned',
      privateDetails = str(status),
    )


OUTGOING_REQUESTS = RequestsMetric(metricId = Metric.KHALEESI_OUTGOING_REQUESTS)
INCOMING_REQUESTS = RequestsMetric(metricId = Metric.KHALEESI_INCOMING_REQUESTS)
