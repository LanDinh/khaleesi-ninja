"""khaleesi.ninja base model which sends events upon changes."""

from __future__ import annotations

# Python.
from typing import Dict, Generic, Tuple, Any

# Django.
from django.conf import settings
from django.db import models

# gRPC.
from google.protobuf.json_format import MessageToJson

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import ObjectMetadata, User
from khaleesi.proto.core_sawmill_pb2 import Event
from .baseModel import Grpc
from .idModel import Model as BaseModel


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA\


class Model(BaseModel[Grpc], Generic[Grpc]):
  """khaleesi.ninja base model which sends events upon changes."""

  khaleesiCreated        = models.DateTimeField(auto_now_add = True)
  khaleesiCreatedById    = models.TextField()
  khaleesiCreatedByType  = models.TextField()
  khaleesiModified       = models.DateTimeField(auto_now = True)
  khaleesiModifiedById   = models.TextField()
  khaleesiModifiedByType = models.TextField()


  @property
  def khaleesiOwner(self) -> User :
    """Get the owner of an instance."""
    user = User()
    user.type = User.UserType.SYSTEM
    user.id   = f'{khaleesiSettings["METADATA"]["GATE"]}-{khaleesiSettings["METADATA"]["SERVICE"]}'
    return user

  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Grpc,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    action  = Event.Action.ActionType.UPDATE
    details = MessageToJson(grpc)

    try:
      # Creation.
      if self._state.adding:
        action = Event.Action.ActionType.CREATE
        self.khaleesiCreatedById   = STATE.request.user.id
        self.khaleesiCreatedByType = User.UserType.Name(STATE.request.user.type)

      # Modification.
      self.khaleesiModifiedById   = STATE.request.user.id
      self.khaleesiModifiedByType = User.UserType.Name(STATE.request.user.type)

      super().khaleesiSave(*args, metadata = metadata, grpc = grpc, **kwargs)

      self._logSuccessEvent(action = action, details = details)

    except Exception:
      self._logFailureEvent(action = action, details = details)
      raise

  def delete(self, *args: Any, **kwargs: Any) -> Tuple[int, Dict[str, int]] :
    action  = Event.Action.ActionType.DELETE
    details = ''
    try:
      result = super().delete(*args, **kwargs)
      self._logSuccessEvent(action = action, details = details)
      return result
    except Exception:
      self._logFailureEvent(action = action, details = details)
      raise


  def toGrpc(self, *, metadata: ObjectMetadata = ObjectMetadata(), grpc: Grpc) -> Grpc :
    """Return a grpc object containing own values."""
    super().toGrpc(metadata = metadata, grpc = grpc)
    metadata.created.FromDatetime(self.khaleesiCreated)
    metadata.createdBy.id   = self.khaleesiCreatedById
    metadata.createdBy.type = User.UserType.Value(self.khaleesiCreatedByType)
    metadata.modified.FromDatetime(self.khaleesiModified)
    metadata.modifiedBy.id   = self.khaleesiModifiedById
    metadata.modifiedBy.type = User.UserType.Value(self.khaleesiModifiedByType)
    return grpc


  def _logSuccessEvent(self, *, action: 'Event.Action.ActionType.V', details : str) -> None :
    """Log a CRUD success event."""
    self._logEvent(action = action, result = Event.Action.ResultType.SUCCESS, details = details)

  def _logFailureEvent(self, *, action: 'Event.Action.ActionType.V', details: str) -> None :
    """Log a CRUD failure event."""
    self._logEvent(action = action, result = Event.Action.ResultType.ERROR, details = details)

  def _logEvent(
      self, *,
      action : 'Event.Action.ActionType.V',
      result : 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log a CRUD event."""
    event = Event()
    event.target.id = self.khaleesiId
    event.target.type = self.modelType()
    event.target.owner.CopyFrom(self.khaleesiOwner)
    event.action.crudType = action
    event.action.result = result
    event.action.details = details
    SINGLETON.structuredLogger.logEvent(event = event)

  class Meta(BaseModel.Meta):
    abstract = True
