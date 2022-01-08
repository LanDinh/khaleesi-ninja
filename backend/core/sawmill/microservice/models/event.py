"""Event logs."""

# Python.
from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent
from microservice.models.abstract import Metadata
from microservice.parse_util import parse_uuid


class EventManager(models.Manager['Event']):
  """Custom model manager."""

  def log_event(self, *, grpc_event: GrpcEvent) -> Event :
    """Log a gRPC event."""
    errors = ''

    target_owner, target_owner_error = parse_uuid(
      raw = grpc_event.target.owner.id,
      name = 'target_owner',
    )
    errors += target_owner_error

    if grpc_event.action.crud_type == GrpcEvent.Action.ActionType.CUSTOM:
      action_type = grpc_event.action.custom_type
    else:
      action_type = GrpcEvent.Action.ActionType.Name(grpc_event.action.crud_type)

    return self.create(
      # Metadata.
      **self.model.log_metadata(metadata = grpc_event.metadata, errors = errors),
      # Target.
      target_type = grpc_event.target.type,
      target_id = grpc_event.target.id,
      target_owner = target_owner,
      # Origin.
      origin_user = grpc_event.request_metadata.user.id,
      origin_type = grpc_event.request_metadata.user.type,
      # Action.
      action_type = action_type,
      action_result = grpc_event.action.result,
      action_details = grpc_event.action.details,
    )


class Event(Metadata):
  """Event logs."""

  # Target.
  target_type  = models.TextField(default = 'UNKNOWN')
  target_id    = models.BigIntegerField(default = 0)
  target_owner = models.UUIDField(null = True, blank = True)

  # Origin.
  origin_user   = models.TextField(default = 'UNKNOWN')
  origin_type   = models.IntegerField(default = 0)

  # Action.
  action_type    = models.TextField(default = 'UNKNOWN')
  action_result  = models.IntegerField(default = 0)
  action_details = models.TextField(default = 'UNKNOWN')

  objects = EventManager()

  def to_grpc_event(self) -> GrpcEvent :
    """Map to gRPC event message."""

    grpc_event = GrpcEvent()
    # Request metadata.
    grpc_event.request_metadata.user.id   = self.origin_user
    grpc_event.request_metadata.user.type = self.origin_type
    # Metadata.
    grpc_event.metadata.timestamp.FromDatetime(self.meta_event_timestamp)
    grpc_event.metadata.logged_timestamp.FromDatetime(self.meta_logged_timestamp)
    grpc_event.metadata.logger.request_id       = self.meta_logger_request_id
    grpc_event.metadata.logger.khaleesi_gate    = self.meta_logger_khaleesi_gate
    grpc_event.metadata.logger.khaleesi_service = self.meta_logger_khaleesi_service
    grpc_event.metadata.logger.grpc_service     = self.meta_logger_grpc_service
    grpc_event.metadata.logger.grpc_method      = self.meta_logger_grpc_method
    # Target.
    grpc_event.target.type     = self.target_type
    grpc_event.target.id       = self.target_id
    if self.target_owner:
      grpc_event.target.owner.id = str(self.target_owner)
    # Action.
    try:
      grpc_event.action.crud_type = GrpcEvent.Action.ActionType.Value(self.action_type)
    except ValueError:
      grpc_event.action.crud_type = GrpcEvent.Action.ActionType.CUSTOM
      grpc_event.action.custom_type = self.action_type
    grpc_event.action.result  = self.action_result  # type: ignore[assignment]
    grpc_event.action.details = self.action_details

    return grpc_event
