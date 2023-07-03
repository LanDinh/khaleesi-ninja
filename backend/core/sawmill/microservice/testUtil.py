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
from microservice.models.logs.abstractResponse import ResponseMetadata


class ModelRequestMetadataMixin:
  """Sawmill test utility."""

  assertEqual: Callable  # type: ignore[type-arg]

  def modelFullRequestMetadata(self, *, user: 'User.UserType.V') -> Dict[str, Any] :
    """Fill model request metadata for testing purposes."""
    return {
        'metaCallerHttpRequestId'  : 'http-request-id',
        'metaCallerGrpcRequestId'  : 'grpc-request-id',
        'metaCallerKhaleesiGate'   : 'khaleesi-gate',
        'metaCallerKhaleesiService': 'khaleesi-service',
        'metaCallerGrpcService'    : 'grpc-service',
        'metaCallerGrpcMethod'     : 'grpc-method',
        'metaCallerPodId'          : 'pod-id',
        'metaUserId'               : 'origin-user',
        'metaUserType'             : user,
        'metaReportedTimestamp'    : datetime.now(tz = timezone.utc),
        'metaLoggedTimestamp'      : datetime.now(tz = timezone.utc),
    }

  def modelEmptyRequestMetadata(self) -> Dict[str, datetime] :
    """Provide necessary model metadata to avoid NPEs."""
    return {
        'metaReportedTimestamp': datetime.now(tz = timezone.utc),
        'metaLoggedTimestamp'  : datetime.now(tz = timezone.utc),
    }

  def assertGrpcRequestMetadata(
      self, *,
      model       : Metadata,
      grpc        : GrpcRequestMetadata,
      grpcResponse: GrpcResponseMetadata,
  ) -> None :
    """Assert that returned gRPC request metadata matches the original model metadata."""
    self.assertEqual(model.metaCallerHttpRequestId  , grpc.httpCaller.requestId)
    self.assertEqual(model.metaCallerGrpcRequestId  , grpc.grpcCaller.requestId)
    self.assertEqual(model.metaCallerKhaleesiGate   , grpc.grpcCaller.khaleesiGate)
    self.assertEqual(model.metaCallerKhaleesiService, grpc.grpcCaller.khaleesiService)
    self.assertEqual(model.metaCallerGrpcService    , grpc.grpcCaller.grpcService)
    self.assertEqual(model.metaCallerGrpcMethod     , grpc.grpcCaller.grpcMethod)
    self.assertEqual(model.metaCallerPodId          , grpc.grpcCaller.podId)
    self.assertEqual(model.metaUserId  , grpc.user.id)
    self.assertEqual(model.metaUserType, grpc.user.type)
    self.assertEqual(
      model.metaReportedTimestamp,
      grpc.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      model.metaLoggedTimestamp,
      grpcResponse.loggedTimestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )


M = TypeVar('M', bound = ResponseMetadata)


class ModelResponseMetadataMixin(ModelRequestMetadataMixin):
  """Sawmill test utility."""

  assertLess: Callable  # type: ignore[type-arg]

  # noinspection PyMethodOverriding
  def modelFullRequestMetadata(  # type: ignore[override]  # pylint: disable=arguments-differ
      self, *,
      user  : 'User.UserType.V',
      status: StatusCode,
  ) -> Dict[str, Any] :
    """Fill model request metadata for testing purposes."""
    return {
        'metaResponseStatus'           : status.name,
        'metaResponseReportedTimestamp': datetime.now(tz = timezone.utc) + timedelta(days = 1),
        'metaResponseLoggedTimestamp'  : datetime.now(tz = timezone.utc) + timedelta(days = 1),
        'metaChildDuration'            : timedelta(hours = 12),
        **super().modelFullRequestMetadata(user = user),
    }

  def modelEmptyRequestMetadata(self) -> Dict[str, datetime] :
    """Provide necessary model metadata to avoid NPEs."""
    return {
        'metaResponseReportedTimestamp': datetime.now(tz = timezone.utc),
        'metaResponseLoggedTimestamp'  : datetime.now(tz = timezone.utc),
        **super().modelEmptyRequestMetadata(),
    }

  @staticmethod
  def getModelForResponseSaving(*, modelType: Type[M]) -> M :
    """Provide a model to be used for response saving tests."""
    start = datetime.now(tz = timezone.utc)
    end   = start + timedelta(days = 1)
    model = modelType(
      metaLoggedTimestamp = start,
      metaReportedTimestamp = start,
      # Logged timestamps get created at save time, which we mock.
      metaResponseLoggedTimestamp = end
    )
    model.save = MagicMock()  # type: ignore[assignment]
    return model

  def assertGrpcResponseMetadata(
      self, *,
      model                : ResponseMetadata,
      grpcResponse         : GrpcResponse,
      grpcResponseResponse : GrpcResponseMetadata,
      grpcResponseProcessed: GrpcProcessedResponse,
  ) -> None :
    """Assert that returned gRPC request metadata matches the original model metadata."""
    self.assertEqual(model.metaResponseStatus, grpcResponse.status)
    self.assertEqual(
      model.metaResponseReportedTimestamp,
      grpcResponse.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      model.metaResponseLoggedTimestamp,
      grpcResponseResponse.loggedTimestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      model.metaChildDuration.total_seconds(),
      grpcResponseProcessed.childDurationAbsolute.seconds,
    )
    self.assertEqual(0.5, round(grpcResponseProcessed.childDurationRelative, 1))
    self.assertLess(0   , grpcResponseProcessed.loggedDuration.nanos)
    self.assertLess(0   , grpcResponseProcessed.reportedDuration.nanos)
