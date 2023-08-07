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
      site           : str             = 'metadata-site',
      app            : str             = 'metadata-app',
      service        : str             = 'metadata-service',
      method         : str             = 'metadata-method',
  ) -> RequestMetadata :
    """Fill gRPC request metadata for testing purposes."""
    requestMetadata.httpCaller.requestId = 'http-request-id'
    requestMetadata.httpCaller.site      = 'amazing-site'
    requestMetadata.httpCaller.path      = '/a/random/path'
    requestMetadata.httpCaller.podId     = 'frontend-pod'
    requestMetadata.grpcCaller.requestId  = 'grpc-request-id'
    requestMetadata.grpcCaller.site       = site
    requestMetadata.grpcCaller.app        = app
    requestMetadata.grpcCaller.service    = service
    requestMetadata.grpcCaller.method     = method
    requestMetadata.grpcCaller.podId      = 'random-pod'
    requestMetadata.user.id   = 'metadata-user-id'
    requestMetadata.user.type = user
    requestMetadata.timestamp.FromDatetime(now)
    return requestMetadata
