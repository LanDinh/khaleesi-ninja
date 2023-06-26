"""Add request metadata to request protobufs."""

# Python.
from datetime import datetime, timezone
from typing import Any, cast

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.proto.core_pb2 import RequestMetadata


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


def addGrpcServerSystemRequestMetadata(
    *,
    request      : Any,
    httpRequestId: str,
    grpcRequestId: str,
    grpcMethod   : str,
) -> None :
  """Add request metadata to request protobufs."""
  _addRequestMetadata(
    request       = request,
    httpRequestId = httpRequestId,
    grpcRequestId = grpcRequestId,
    grpcService   = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME'],
    grpcMethod    = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES'][grpcMethod]['METHOD'],  # type: ignore[literal-required]  # pylint: disable=line-too-long
    userId        = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['USER_ID'],
    userType      = UserType.SYSTEM,
  )

def addRequestMetadata(*, request : Any) -> None :
  """Add request metadata to request protobufs."""
  _addRequestMetadata(
    request       = request,
    httpRequestId = STATE.request.httpRequestId,
    grpcRequestId = STATE.request.grpcRequestId,
    grpcService   = STATE.request.grpcService,
    grpcMethod    = STATE.request.grpcMethod,
    userId        = STATE.user.userId,
    userType      = STATE.user.type,
  )

def _addRequestMetadata(
    *,
    request      : Any,
    httpRequestId: str,
    grpcRequestId: str,
    grpcService  : str,
    grpcMethod   : str,
    userId       : str,
    userType     : UserType,
) -> None :
  """Add request metadata to request protobufs."""
  requestMetadata = cast(RequestMetadata, request.requestMetadata)
  requestMetadata.caller.httpRequestId   = httpRequestId
  requestMetadata.caller.grpcRequestId   = grpcRequestId
  requestMetadata.caller.khaleesiGate    = khaleesiSettings['METADATA']['GATE']
  requestMetadata.caller.khaleesiService = khaleesiSettings['METADATA']['SERVICE']
  requestMetadata.caller.grpcService     = grpcService
  requestMetadata.caller.grpcMethod      = grpcMethod
  requestMetadata.caller.podId           = khaleesiSettings['METADATA']['POD_ID']
  requestMetadata.user.id                = userId
  requestMetadata.user.type              = userType.value  # type: ignore[assignment]
  requestMetadata.timestamp.FromDatetime(datetime.now(tz = timezone.utc))
