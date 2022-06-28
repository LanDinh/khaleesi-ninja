"""gRPC test utility."""

# Python.
from datetime import datetime, timezone

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata, User  # pylint: disable=unused-import


class GrpcTestMixin:
  """gRPC test utility."""

  def set_request_metadata(
      self, *,
      request_metadata: RequestMetadata   = RequestMetadata(),
      now             : datetime          = datetime.now(tz = timezone.utc),
      user            : 'User.UserType.V',
      khaleesi_gate   : str               = 'metadata-khaleesi-gate',
      khaleesi_service: str               = 'metadata-khaleesi-service',
      grpc_service    : str               = 'metadata-grpc-service',
      grpc_method     : str               = 'metadata-grpc-method',
  ) -> RequestMetadata :
    """Fill gRPC request metadata for testing purposes."""
    request_metadata.caller.request_id       = 1337
    request_metadata.caller.khaleesi_gate    = khaleesi_gate
    request_metadata.caller.khaleesi_service = khaleesi_service
    request_metadata.caller.grpc_service     = grpc_service
    request_metadata.caller.grpc_method      = grpc_method
    request_metadata.user.id   = 'metadata-user-id'
    request_metadata.user.type = user
    request_metadata.timestamp.FromDatetime(now)
    return request_metadata
