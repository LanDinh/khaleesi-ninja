"""Event logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent, EventResponse as GrpcEventResponse
from microservice.models.abstract import Metadata
from microservice.parse_util import parse_string


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class EventManager(models.Manager['Event']):
  """Custom model manager."""

  def log_event(self, *, grpc_event: GrpcEvent) -> Event :
    """Log a gRPC event."""
    # If this is a server startup event, we need to do the metric logging here.
    if grpc_event.target.type == \
        khaleesi_settings['GRPC']['SERVER_METHOD_NAMES']['LIFECYCLE']['TARGET'] \
        and grpc_event.action.crud_type in \
        [ GrpcEvent.Action.ActionType.START, GrpcEvent.Action.ActionType.END ]:
      AUDIT_EVENT.inc(event = grpc_event)

    errors: List[str] = []

    return self.create(
      # Target.
      target_type = parse_string(
        raw = grpc_event.target.type,
        name = 'target_type',
        errors = errors,
      ),
      target_id = parse_string(
        raw  = grpc_event.target.id,
        name = 'target_id',
        errors = errors,
      ),
      target_owner = parse_string(
        raw  = grpc_event.target.owner.id,
        name = 'target_owner',
        errors = errors,
      ),
      # Action.
      action_crud_type   = grpc_event.action.crud_type,
      action_custom_type = grpc_event.action.custom_type,
      action_result      = grpc_event.action.result,
      action_details = parse_string(
        raw = grpc_event.action.details,
        name = 'action_details',
        errors = errors,
      ),
      # Metadata.
      **self.model.log_metadata(metadata = grpc_event.request_metadata, errors = errors),
    )


class Event(Metadata):
  """Event logs."""

  # Target.
  target_type  = models.TextField(default = 'UNKNOWN')
  target_id    = models.TextField(default = 'UNKNOWN')
  target_owner = models.TextField(default = 'UNKNOWN')

  # Action.
  action_crud_type   = models.IntegerField(default = 0)
  action_custom_type = models.TextField(default = 'UNKNOWN')
  action_result      = models.IntegerField(default = 0)
  action_details     = models.TextField(default = 'UNKNOWN')

  objects = EventManager()

  def to_grpc_event_response(self) -> GrpcEventResponse :
    """Map to gRPC event message."""

    grpc_event_response = GrpcEventResponse()
    self.request_metadata_to_grpc(request_metadata = grpc_event_response.event.request_metadata)
    self.response_metadata_to_grpc(response_metadata = grpc_event_response.event_metadata)
    # Target.
    grpc_event_response.event.target.type = self.target_type
    grpc_event_response.event.target.id   = self.target_id
    grpc_event_response.event.target.owner.id = self.target_owner
    # Action.
    grpc_event_response.event.action.crud_type   = self.action_crud_type  # type: ignore[assignment]
    grpc_event_response.event.action.custom_type = self.action_custom_type
    grpc_event_response.event.action.result      = self.action_result  # type: ignore[assignment]
    grpc_event_response.event.action.details     = self.action_details

    return grpc_event_response
