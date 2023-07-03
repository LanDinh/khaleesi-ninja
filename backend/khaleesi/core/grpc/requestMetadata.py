"""Add request metadata to request protobufs."""

# Python.
from datetime import datetime, timezone

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import RequestMetadata, User


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


def addSystemRequestMetadata(
    *,
    metadata     : RequestMetadata,
    httpRequestId: str,
    grpcRequestId: str,
    grpcMethod   : str,
) -> None :
  """Add request metadata to request protobufs."""
  systemConfiguration = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']

  # Systems won't call HTTP endpoints directly.
  metadata.httpCaller.requestId    = httpRequestId
  metadata.httpCaller.khaleesiGate = khaleesiSettings['METADATA']['GATE']
  metadata.httpCaller.path         = '/'
  metadata.httpCaller.podId        = ''

  # gRPC details are specified in the configuration.
  metadata.grpcCaller.requestId    = grpcRequestId
  metadata.grpcCaller.grpcService  = systemConfiguration['SERVICE_NAME']
  metadata.grpcCaller.grpcMethod   = systemConfiguration[grpcMethod]['METHOD']  # type: ignore[literal-required]  # pylint: disable=line-too-long

  # User details are specified in the configuration.
  metadata.user.id   = systemConfiguration['USER_ID']
  metadata.user.type = User.UserType.SYSTEM
  _addCommonRequestMetadata(metadata = metadata)

def addRequestMetadata(*, metadata : RequestMetadata) -> None :
  """Add request metadata to request protobufs."""
  metadata.CopyFrom(STATE.request)
  _addCommonRequestMetadata(metadata = metadata)

def _addCommonRequestMetadata(*, metadata: RequestMetadata) -> None :
  """Add request metadata to request protobufs."""
  metadata.grpcCaller.khaleesiGate    = khaleesiSettings['METADATA']['GATE']
  metadata.grpcCaller.khaleesiService = khaleesiSettings['METADATA']['SERVICE']
  metadata.grpcCaller.podId           = khaleesiSettings['METADATA']['POD_ID']
  metadata.timestamp.FromDatetime(datetime.now(tz = timezone.utc))
