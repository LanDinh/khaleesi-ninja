"""gRPC test utility."""

# Python.
from datetime import datetime, timezone

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata, User  # pylint: disable=unused-import


class GrpcTestMixin:
  """gRPC test utility."""

  def setRequestMetadata(
      self, *,
      requestMetadata: RequestMetadata = RequestMetadata(),
      now            : datetime        = datetime.now(tz = timezone.utc),
      user           : 'User.UserType.V',
      khaleesiGate   : str             = 'metadata-khaleesi-gate',
      khaleesiService: str             = 'metadata-khaleesi-service',
      grpcService    : str             = 'metadata-grpc-service',
      grpcMethod     : str             = 'metadata-grpc-method',
  ) -> RequestMetadata :
    """Fill gRPC request metadata for testing purposes."""
    requestMetadata.httpCaller.requestId    = 'http-request-id'
    requestMetadata.httpCaller.khaleesiGate = 'amazing-gate'
    requestMetadata.httpCaller.path         = '/a/random/path'
    requestMetadata.httpCaller.podId        = 'frontend-pod'
    requestMetadata.grpcCaller.requestId       = 'grpc-request-id'
    requestMetadata.grpcCaller.khaleesiGate    = khaleesiGate
    requestMetadata.grpcCaller.khaleesiService = khaleesiService
    requestMetadata.grpcCaller.grpcService     = grpcService
    requestMetadata.grpcCaller.grpcMethod      = grpcMethod
    requestMetadata.grpcCaller.podId           = 'random-pod'
    requestMetadata.user.id   = 'metadata-user-id'
    requestMetadata.user.type = user
    requestMetadata.timestamp.FromDatetime(now)
    return requestMetadata
