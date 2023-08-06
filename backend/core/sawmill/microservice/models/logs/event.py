"""Event logs."""

from __future__ import annotations

# Python.
from typing import List, Any

# Django.
from django.db import models
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Manager
from khaleesi.core.models.idModel import Model
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_pb2 import User, ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent, EventRequest as GrpcEventRequest
from microservice.models.logs.metadataMixin import GrpcMetadataMixin


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Event(Model[GrpcEventRequest], GrpcMetadataMixin):
  """Event logs."""
  khaleesiId = models.TextField(unique = False, editable = False)  # Avoid index building.

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

  objects: Manager[Event]


  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcEventRequest,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    errors: List[str] = []

    if self._state.adding:
      # Target.
      self.targetType = parseString(
        raw    = grpc.event.target.type,
        name   = 'targetType',
        errors = errors,
      )
      self.targetId = parseString(raw = grpc.event.target.id, name = 'targetId', errors = errors)
      self.targetOwnerId = parseString(
        raw    = grpc.event.target.owner.id,
        name   = 'targetOwner',
        errors = errors,
      )
      self.targetOwnerType = User.UserType.Name(grpc.event.target.owner.type)

      # Action.
      self.actionCrudType   = GrpcEvent.Action.ActionType.Name(grpc.event.action.crudType)
      self.actionCustomType = grpc.event.action.customType
      self.actionResult     = GrpcEvent.Action.ResultType.Name(grpc.event.action.result)
      self.actionDetails    = grpc.event.action.details

    # Needs to be at the end because it saves errors to the model.
    self.metadataFromGrpc(grpc = grpc.requestMetadata, errors = errors)
    super().khaleesiSave(*args, metadata = metadata, grpc = grpc, **kwargs)

  def toGrpc(self) -> GrpcEventRequest :
    """Return a grpc object containing own values."""
    grpc = GrpcEventRequest()
    self.metadataToGrpc(logMetadata = grpc.logMetadata, requestMetadata = grpc.requestMetadata)

    # Target.
    grpc.event.target.type       = self.targetType
    grpc.event.target.id         = self.targetId
    grpc.event.target.owner.id   = self.targetOwnerId
    grpc.event.target.owner.type = User.UserType.Value(self.targetOwnerType)

    # Action.
    grpc.event.action.crudType   = GrpcEvent.Action.ActionType.Value(self.actionCrudType)
    grpc.event.action.customType = self.actionCustomType
    grpc.event.action.result     = GrpcEvent.Action.ResultType.Value(self.actionResult)
    grpc.event.action.details    = self.actionDetails

    return grpc
