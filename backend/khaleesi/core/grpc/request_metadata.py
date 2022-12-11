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


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


def add_grpc_server_system_request_metadata(
    *,
    request     : Any,
    grpc_method : str,
) -> None :
  """Add request metadata to request protobufs."""
  _add_request_metadata(
    request      = request,
    request_id   = 'system',
    grpc_service = khaleesi_settings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME'],
    grpc_method  = khaleesi_settings['GRPC']['SERVER_METHOD_NAMES'][grpc_method]['METHOD'],  # type: ignore[literal-required]  # pylint: disable=line-too-long
    user_id      = khaleesi_settings['GRPC']['SERVER_METHOD_NAMES']['USER_ID'],
    user_type    = UserType.SYSTEM,
  )

def add_request_metadata(*, request : Any) -> None :
  """Add request metadata to request protobufs."""
  _add_request_metadata(
    request      = request,
    request_id   = STATE.request.id,
    grpc_service = STATE.request.grpc_service,
    grpc_method  = STATE.request.grpc_method,
    user_id      = STATE.user.id,
    user_type    = STATE.user.type,
  )

def _add_request_metadata(
    *,
    request     : Any,
    request_id  : str,
    grpc_service: str,
    grpc_method : str,
    user_id     : str,
    user_type   : UserType,
) -> None :
  """Add request metadata to request protobufs."""
  request_metadata = cast(RequestMetadata, request.request_metadata)
  request_metadata.caller.request_id       = request_id
  request_metadata.caller.khaleesi_gate    = khaleesi_settings['METADATA']['GATE']
  request_metadata.caller.khaleesi_service = khaleesi_settings['METADATA']['SERVICE']
  request_metadata.caller.grpc_service     = grpc_service
  request_metadata.caller.grpc_method      = grpc_method
  request_metadata.user.id                 = user_id
  request_metadata.user.type               = user_type.value  # type: ignore[assignment]
  request_metadata.timestamp.FromDatetime(datetime.now(tz = timezone.utc))
