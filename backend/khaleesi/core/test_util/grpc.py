"""gRPC test utility."""

# Python.
from datetime import datetime

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata, User


class GrpcTestMixin:
  """gRPC test utility."""

  @staticmethod
  def set_request_metadata(
      *,
      request_metadata: RequestMetadata,
      now: datetime,
      user: 'User.UserType.V',
  ) -> None :
    """Fill gRPC request metadata for testing purposes."""
    request_metadata.caller.request_id       = 1337
    request_metadata.caller.khaleesi_gate    = 'metadata-khaleesi-gate'
    request_metadata.caller.khaleesi_service = 'metadata-khaleesi-service'
    request_metadata.caller.grpc_service     = 'metadata-grpc-service'
    request_metadata.caller.grpc_method      = 'metadata-grpc-method'
    request_metadata.user.id   = 'origin-system'
    request_metadata.user.type = user
    request_metadata.timestamp.FromDatetime(now)
