"""Sawmill test utility."""

# Python.
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Callable, TypeVar, Type

# gRPC.
from unittest.mock import MagicMock

from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata as GrpcRequestMetadata, User  # pylint: disable=unused-import
from khaleesi.proto.core_sawmill_pb2 import (
  ResponseMetadata as GrpcResponseMetadata,
  Response as GrpcResponse,
  ProcessedResponse as GrpcProcessedResponse,
)
from microservice.models.logs.abstract import Metadata
from microservice.models.logs.abstract_response import ResponseMetadata


class ModelRequestMetadataMixin:
  """Sawmill test utility."""

  assertEqual: Callable  # type: ignore[type-arg]

  def model_full_request_metadata(self, *, user: 'User.UserType.V') -> Dict[str, Any] :
    """Fill model request metadata for testing purposes."""
    return {
        'meta_caller_request_id'      : '1337',
        'meta_caller_khaleesi_gate'   : 'khaleesi-gate',
        'meta_caller_khaleesi_service': 'khaleesi-service',
        'meta_caller_grpc_service'    : 'grpc-service',
        'meta_caller_grpc_method'     : 'grpc-method',
        'meta_caller_pod_id'          : 'pod_id',
        'meta_user_id'                : 'origin-user',
        'meta_user_type'              : user,
        'meta_reported_timestamp'     : datetime.now(tz = timezone.utc),
        'meta_logged_timestamp'       : datetime.now(tz = timezone.utc),
    }

  def model_empty_request_metadata(self) -> Dict[str, datetime] :
    """Provide necessary model metadata to avoid NPEs."""
    return {
        'meta_reported_timestamp': datetime.now(tz = timezone.utc),
        'meta_logged_timestamp'  : datetime.now(tz = timezone.utc),
    }

  def assert_grpc_request_metadata(
      self, *,
      model        : Metadata,
      grpc         : GrpcRequestMetadata,
      grpc_response: GrpcResponseMetadata,
  ) -> None :
    """Assert that returned gRPC request metadata matches the original model metadata."""
    self.assertEqual(model.meta_caller_request_id      , grpc.caller.request_id)
    self.assertEqual(model.meta_caller_khaleesi_gate   , grpc.caller.khaleesi_gate)
    self.assertEqual(model.meta_caller_khaleesi_service, grpc.caller.khaleesi_service)
    self.assertEqual(model.meta_caller_grpc_service    , grpc.caller.grpc_service)
    self.assertEqual(model.meta_caller_grpc_method     , grpc.caller.grpc_method)
    self.assertEqual(model.meta_caller_pod_id          , grpc.caller.pod_id)
    self.assertEqual(model.meta_user_id  , grpc.user.id)
    self.assertEqual(model.meta_user_type, grpc.user.type)
    self.assertEqual(
      model.meta_reported_timestamp,
      grpc.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      model.meta_logged_timestamp,
      grpc_response.logged_timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )


M = TypeVar('M', bound = ResponseMetadata)


class ModelResponseMetadataMixin(ModelRequestMetadataMixin):
  """Sawmill test utility."""

  assertLess: Callable  # type: ignore[type-arg]

  # noinspection PyMethodOverriding
  def model_full_request_metadata(  # type: ignore[override]  # pylint: disable=arguments-differ
      self, *,
      user  : 'User.UserType.V',
      status: StatusCode,
  ) -> Dict[str, Any] :
    """Fill model request metadata for testing purposes."""
    return {
        'meta_response_status'            : status.name,
        'meta_response_reported_timestamp': datetime.now(tz = timezone.utc) + timedelta(days = 1),
        'meta_response_logged_timestamp'  : datetime.now(tz = timezone.utc) + timedelta(days = 1),
        **super().model_full_request_metadata(user = user),
    }

  def model_empty_request_metadata(self) -> Dict[str, datetime] :
    """Provide necessary model metadata to avoid NPEs."""
    return {
        'meta_response_reported_timestamp': datetime.now(tz = timezone.utc),
        'meta_response_logged_timestamp'  : datetime.now(tz = timezone.utc),
        **super().model_empty_request_metadata(),
    }

  @staticmethod
  def get_model_for_response_saving(*, model_type: Type[M]) -> M :
    """Provide a model to be used for response saving tests."""
    start = datetime.now(tz = timezone.utc)
    end   = start + timedelta(days = 1)
    model = model_type(
      meta_logged_timestamp = start,
      meta_reported_timestamp = start,
      # Logged timestamps get created at save time, which we mock.
      meta_response_logged_timestamp = end
    )
    model.save = MagicMock()  # type: ignore[assignment]
    return model

  def assert_grpc_response_metadata(
      self, *,
      model                  : ResponseMetadata,
      grpc_response          : GrpcResponse,
      grpc_response_response : GrpcResponseMetadata,
      grpc_response_processed: GrpcProcessedResponse,
  ) -> None :
    """Assert that returned gRPC request metadata matches the original model metadata."""
    self.assertEqual(model.meta_response_status, grpc_response.status)
    self.assertEqual(
      model.meta_response_reported_timestamp,
      grpc_response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      model.meta_response_logged_timestamp,
      grpc_response_response.logged_timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertLess(0, grpc_response_processed.logged_duration.nanos)
    self.assertLess(0, grpc_response_processed.reported_duration.nanos)
