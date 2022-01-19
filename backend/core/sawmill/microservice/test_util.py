"""Sawmill test utility."""

# Python.
from datetime import datetime, timezone
from typing import Dict, Any, Callable

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata, User  # pylint: disable=unused-import
from khaleesi.proto.core_sawmill_pb2 import ResponseMetadata
from microservice.models.abstract import Metadata


class ModelRequestMetadataMixin:
  """Sawmill test utility."""

  assertEqual: Callable  # type: ignore[type-arg]

  @staticmethod
  def model_full_request_metadata(*, user: 'User.UserType.V') -> Dict[str, Any] :
    """Fill model request metadata for testing purposes."""
    return {
        'meta_caller_request_id'      : 1337,
        'meta_caller_khaleesi_gate'   : 'khaleesi-gate',
        'meta_caller_khaleesi_service': 'khaleesi-service',
        'meta_caller_grpc_service'    : 'grpc-service',
        'meta_caller_grpc_method'     : 'grpc-method',
        'meta_user_id'                : 'origin-user',
        'meta_user_type'              : user,
        'meta_event_timestamp'        : datetime.now(tz = timezone.utc),
        'meta_logged_timestamp'       : datetime.now(tz = timezone.utc),
    }

  @staticmethod
  def model_empty_request_metadata() -> Dict[str, datetime] :
    """Provide necessary model metadata to avoid NPEs."""
    return {
        'meta_event_timestamp' : datetime.now(tz = timezone.utc),
        'meta_logged_timestamp': datetime.now(tz = timezone.utc),
    }

  def assert_grpc_request_metadata(
      self, *,
      model: Metadata,
      grpc: RequestMetadata,
      grpc_response: ResponseMetadata,
  ) -> None :
    """Assert that returned gRPC request metadata matches the original model metadata."""
    self.assertEqual(model.meta_caller_request_id      , grpc.caller.request_id)
    self.assertEqual(model.meta_caller_khaleesi_gate   , grpc.caller.khaleesi_gate)
    self.assertEqual(model.meta_caller_khaleesi_service, grpc.caller.khaleesi_service)
    self.assertEqual(model.meta_caller_grpc_service    , grpc.caller.grpc_service)
    self.assertEqual(model.meta_caller_grpc_method     , grpc.caller.grpc_method)
    self.assertEqual(model.meta_user_id  , grpc.user.id)
    self.assertEqual(model.meta_user_type, grpc.user.type)
    self.assertEqual(
      model.meta_event_timestamp,
      grpc.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      model.meta_logged_timestamp,
      grpc_response.logged_timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
