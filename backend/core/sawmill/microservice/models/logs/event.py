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
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent, EventResponse as GrpcEventResponse
from microservice.models.logs.abstract import Metadata
from khaleesi.core.shared.parse_util import parse_string


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class EventManager(models.Manager['Event']):
  """Custom model manager."""

  def log_event(self, *, grpc_event: GrpcEvent) -> Event :
    """Log a gRPC event."""
    if grpc_event.logger_send_metric:
      AUDIT_EVENT.inc(event = grpc_event)

    errors: List[str] = []

    return self.create(
      event_id = parse_string(raw = grpc_event.id, name = 'event_id', errors = errors),
      # Target.
      target_type = parse_string(
        raw    = grpc_event.target.type,
        name   = 'target_type',
        errors = errors,
      ),
      target_id = parse_string(
        raw    = grpc_event.target.id,
        name   = 'target_id',
        errors = errors,
      ),
      target_owner_id = parse_string(
        raw    = grpc_event.target.owner.id,
        name   = 'target_owner',
        errors = errors,
      ),
      target_owner_type = User.UserType.Name(grpc_event.target.owner.type),
      # Action.
      action_crud_type   = GrpcEvent.Action.ActionType.Name(grpc_event.action.crud_type),
      action_custom_type = grpc_event.action.custom_type,
      action_result      = GrpcEvent.Action.ResultType.Name(grpc_event.action.result),
      action_details     = grpc_event.action.details,
      # Metadata.
      **self.model.log_metadata(metadata = grpc_event.request_metadata, errors = errors),
    )


class Event(Metadata):
  """Event logs."""
  event_id = models.TextField(default = 'UNKNOWN')

  # Target.
  target_type       = models.TextField(default = 'UNKNOWN')
  target_id         = models.TextField(default = 'UNKNOWN')
  target_owner_id   = models.TextField(default = 'UNKNOWN')
  target_owner_type = models.TextField(default = 'UNKNOWN')

  # Action.
  action_crud_type   = models.TextField(default = 'UNKNOWN_ACTION')
  action_custom_type = models.TextField(default = 'UNKNOWN')
  action_result      = models.TextField(default = 'UNKNOWN_RESULT')
  action_details     = models.TextField(default = 'UNKNOWN')

  objects = EventManager()

  def to_grpc_event_response(self) -> GrpcEventResponse :
    """Map to gRPC event message."""

    grpc_event_response = GrpcEventResponse()
    self.request_metadata_to_grpc(request_metadata = grpc_event_response.event.request_metadata)
    self.response_metadata_to_grpc(response_metadata = grpc_event_response.event_metadata)
    grpc_event_response.event.id = self.event_id
    # Target.
    grpc_event_response.event.target.type       = self.target_type
    grpc_event_response.event.target.id         = self.target_id
    grpc_event_response.event.target.owner.id   = self.target_owner_id
    grpc_event_response.event.target.owner.type = User.UserType.Value(self.target_owner_type)
    # Action.
    grpc_event_response.event.action.crud_type =\
        GrpcEvent.Action.ActionType.Value(self.action_crud_type)
    grpc_event_response.event.action.custom_type = self.action_custom_type
    grpc_event_response.event.action.result =\
        GrpcEvent.Action.ResultType.Value(self.action_result)
    grpc_event_response.event.action.details = self.action_details

    return grpc_event_response
