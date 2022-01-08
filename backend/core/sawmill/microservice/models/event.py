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
      action_type = str(grpc_event.action.crud_type)

    return self.create(
      # Metadata.
      **self.model.log_metadata(metadata = grpc_event.metadata, errors = errors),
      # Target.
      target_type = grpc_event.target.type,
      target_id = grpc_event.target.id,
      target_owner = target_owner,
      # Origin.
      origin_user = grpc_event.request_metadata.user.id,
      origin_type = str(grpc_event.request_metadata.user.type),
      # Action.
      action_type = action_type,
      action_result = str(grpc_event.action.result),
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
  origin_type   = models.TextField(default = 'UNKNOWN')

  # Action.
  action_type    = models.TextField(default = 'UNKNOWN')
  action_result  = models.TextField(default = 'UNKNOWN')
  action_details = models.TextField(default = 'UNKNOWN')

  objects = EventManager()
