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
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent, EventResponse as GrpcEventResponse
from microservice.models.logs.abstract import Metadata


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class EventManager(models.Manager['Event']):
  """Custom model manager."""

  def logEvent(self, *, grpcEvent: GrpcEvent) -> Event :
    """Log a gRPC event."""
    if grpcEvent.loggerSendMetric:
      AUDIT_EVENT.inc(event = grpcEvent)

    errors: List[str] = []

    return self.create(
      eventId = parseString(raw = grpcEvent.id, name = 'eventId', errors = errors),
      # Target.
      targetType = parseString(raw = grpcEvent.target.type, name = 'targetType', errors = errors),
      targetId   = parseString(raw = grpcEvent.target.id, name = 'targetId', errors = errors),
      targetOwnerId = parseString(
        raw    = grpcEvent.target.owner.id,
        name   = 'targetOwner',
        errors = errors,
      ),
      targetOwnerType = User.UserType.Name(grpcEvent.target.owner.type),
      # Action.
      actionCrudType   = GrpcEvent.Action.ActionType.Name(grpcEvent.action.crudType),
      actionCustomType = grpcEvent.action.customType,
      actionResult     = GrpcEvent.Action.ResultType.Name(grpcEvent.action.result),
      actionDetails    = grpcEvent.action.details,
      # Metadata.
      **self.model.logMetadata(metadata = grpcEvent.requestMetadata, errors = errors),
    )


class Event(Metadata):
  """Event logs."""
  eventId = models.TextField(default = 'UNKNOWN')

  # Target.
  targetType      = models.TextField(default = 'UNKNOWN')
  targetId        = models.TextField(default = 'UNKNOWN')
  targetOwnerId   = models.TextField(default = 'UNKNOWN')
  targetOwnerType = models.TextField(default = 'UNKNOWN')

  # Action.
  actionCrudType   = models.TextField(default = 'UNKNOWN_ACTION')
  actionCustomType = models.TextField(default = 'UNKNOWN')
  actionResult     = models.TextField(default = 'UNKNOWN_RESULT')
  actionDetails    = models.TextField(default = 'UNKNOWN')

  objects = EventManager()

  def toGrpc(self) -> GrpcEventResponse :
    """Map to gRPC event message."""

    grpcEventResponse = GrpcEventResponse()
    self.requestMetadataToGrpc(requestMetadata = grpcEventResponse.event.requestMetadata)
    self.responseMetadataToGrpc(responseMetadata = grpcEventResponse.eventMetadata)
    grpcEventResponse.event.id = self.eventId
    # Target.
    grpcEventResponse.event.target.type       = self.targetType
    grpcEventResponse.event.target.id         = self.targetId
    grpcEventResponse.event.target.owner.id   = self.targetOwnerId
    grpcEventResponse.event.target.owner.type = User.UserType.Value(self.targetOwnerType)
    # Action.
    grpcEventResponse.event.action.crudType = GrpcEvent.Action.ActionType.Value(self.actionCrudType)
    grpcEventResponse.event.action.customType = self.actionCustomType
    grpcEventResponse.event.action.result     = GrpcEvent.Action.ResultType.Value(self.actionResult)
    grpcEventResponse.event.action.details    = self.actionDetails

    return grpcEventResponse
