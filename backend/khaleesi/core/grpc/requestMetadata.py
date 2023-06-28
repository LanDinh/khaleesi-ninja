"""Add request metadata to request protobufs."""

# Python.
from datetime import datetime, timezone

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.proto.core_pb2 import RequestMetadata


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


def addGrpcServerSystemRequestMetadata(
    *,
    metadata     : RequestMetadata,
    httpRequestId: str,
    grpcRequestId: str,
    grpcMethod   : str,
) -> None :
  """Add request metadata to request protobufs."""
  _addRequestMetadata(
    metadata      = metadata,
    httpRequestId = httpRequestId,
    grpcRequestId = grpcRequestId,
    grpcService   = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME'],
    grpcMethod    = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES'][grpcMethod]['METHOD'],  # type: ignore[literal-required]  # pylint: disable=line-too-long
    userId        = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['USER_ID'],
    userType      = UserType.SYSTEM,
  )

def addRequestMetadata(*, metadata : RequestMetadata) -> None :
  """Add request metadata to request protobufs."""
  _addRequestMetadata(
    metadata      = metadata,
    httpRequestId = STATE.request.httpRequestId,
    grpcRequestId = STATE.request.grpcRequestId,
    grpcService   = STATE.request.grpcService,
    grpcMethod    = STATE.request.grpcMethod,
    userId        = STATE.user.userId,
    userType      = STATE.user.type,
  )

def _addRequestMetadata(
    *,
    metadata     : RequestMetadata,
    httpRequestId: str,
    grpcRequestId: str,
    grpcService  : str,
    grpcMethod   : str,
    userId       : str,
    userType     : UserType,
) -> None :
  """Add request metadata to request protobufs."""
  metadata.caller.httpRequestId   = httpRequestId
  metadata.caller.grpcRequestId   = grpcRequestId
  metadata.caller.khaleesiGate    = khaleesiSettings['METADATA']['GATE']
  metadata.caller.khaleesiService = khaleesiSettings['METADATA']['SERVICE']
  metadata.caller.grpcService     = grpcService
  metadata.caller.grpcMethod      = grpcMethod
  metadata.caller.podId           = khaleesiSettings['METADATA']['POD_ID']
  metadata.user.id                = userId
  metadata.user.type              = userType.value  # type: ignore[assignment]
  metadata.timestamp.FromDatetime(datetime.now(tz = timezone.utc))
