"""Add request metadata to request protobufs."""

# Python.
from datetime import datetime, timezone
from typing import Any, cast

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.proto.core_pb2 import User, RequestMetadata  # pylint: disable=unused-import


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


def add_request_metadata(
    *,
    request     : Any,
    request_id  : str,
    grpc_service: str,
    grpc_method : str,
    user_id     : str,
    user_type   : 'User.UserType.V',
) -> None :
  """Add request metadata to request protobufs."""
  _add_request_metadata(
    request_metadata = cast(RequestMetadata, request.request_metadata),
    request_id       = request_id,
    grpc_service     = grpc_service,
    grpc_method      = grpc_method,
    user_id          = user_id,
    user_type        = user_type,
  )

def _add_request_metadata(
    *,
    request_metadata: RequestMetadata,
    request_id      : str,
    grpc_service    : str,
    grpc_method     : str,
    user_id         : str,
    user_type       : 'User.UserType.V',
) -> None :
  """Add request metadata to request protobufs."""
  request_metadata.caller.request_id       = request_id
  request_metadata.caller.khaleesi_gate    = khaleesi_settings['METADATA']['GATE']
  request_metadata.caller.khaleesi_service = khaleesi_settings['METADATA']['SERVICE']
  request_metadata.caller.grpc_service     = grpc_service
  request_metadata.caller.grpc_method      = grpc_method
  request_metadata.user.id                 = user_id
  request_metadata.user.type               = user_type
  request_metadata.timestamp.FromDatetime(datetime.now(tz = timezone.utc))
