"""Sawmill test utility."""

# Python.
from datetime import datetime, timezone
from typing import Dict, Any

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata, User
from microservice.models.abstract import Metadata


def model_request_metadata(*, user: 'User.UserType.V') -> Dict[str, Any] :
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

def assert_grpc_request_metadata(*, model: Metadata, grpc: RequestMetadata) -> None :
  """Assert that returned gRPC request metadata matches the original model metadata."""

