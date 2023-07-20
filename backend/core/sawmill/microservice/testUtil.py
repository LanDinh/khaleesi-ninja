"""Sawmill test utility."""

# Python.
from datetime import datetime, timezone
from typing import Dict, Any, Callable

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata as GrpcRequestMetadata, User  # pylint: disable=unused-import
from khaleesi.proto.core_sawmill_pb2 import ResponseMetadata as GrpcResponseMetadata
from microservice.models.logs.abstract import Metadata


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
