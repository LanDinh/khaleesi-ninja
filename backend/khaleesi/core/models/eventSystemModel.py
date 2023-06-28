"""khaleesi.ninja base model which sends events upon changes."""

from __future__ import annotations

# Python.
from abc import ABC
from typing import Generic

# Django.
from django.conf import settings

# gRPC.
from google.protobuf.json_format import MessageToJson

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.proto.core_pb2 import ObjectMetadata, User
from khaleesi.proto.core_sawmill_pb2 import Event
from .baseModel import Model as BaseModel, ModelManager as BaseModelManager, Grpc, AbstractModelMeta


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA

class ModelManager(BaseModelManager[Grpc], Generic[Grpc]):
  """khaleesi.ninja base model manager which sends events upon changes."""

  def khaleesiCreate(self, *, grpc: Grpc) -> 'Model'[Grpc] :  # pylint: disable=invalid-sequence-index
    """Create a new instance."""
    try:
      instance = super().khaleesiCreate(grpc = grpc)
      self._logSuccessEvent(instance = instance, action = Event.Action.ActionType.CREATE)  # type: ignore[arg-type]  # pylint: disable=line-too-long
      return instance  # type: ignore[return-value]
    except Exception:
      self._logFailureEvent(
        metadata = ObjectMetadata(),
        action   = Event.Action.ActionType.CREATE,
        details  = MessageToJson(grpc),
      )
      raise

  def khaleesiUpdate(self, *, metadata: ObjectMetadata, grpc: Grpc) -> 'Model'[Grpc] :  # pylint: disable=invalid-sequence-index
    """Update an existing instance."""
    try:
      instance = super().khaleesiUpdate(metadata = metadata, grpc = grpc)
      self._logSuccessEvent(instance = instance, action = Event.Action.ActionType.UPDATE)  # type: ignore[arg-type]  # pylint: disable=line-too-long
      return instance  # type: ignore[return-value]
    except Exception:
      self._logFailureEvent(
        metadata = metadata,
        action   = Event.Action.ActionType.UPDATE,
        details  = MessageToJson(grpc),
      )
      raise

  def khaleesiDelete(self, *, metadata: ObjectMetadata) -> None :
    """Delete an existing instance."""
    try:
      super().khaleesiDelete(metadata = metadata)
      self._logEvent(
        target = metadata.id,
        action = Event.Action.ActionType.DELETE,
        result = Event.Action.ResultType.SUCCESS,
        details = ''
      )
    except Exception:
      self._logFailureEvent(
        metadata = metadata,
        action   = Event.Action.ActionType.DELETE,
        details  = '',
      )
      raise


  def _logSuccessEvent(
      self, *,
      instance: 'Model'[Grpc],   # pylint: disable=invalid-sequence-index
      action  : 'Event.Action.ActionType.V',
  ) -> None :
    """Log a CRUD success event."""
    self._logEvent(
      target = instance.khaleesiId,
      action = action,
      result = Event.Action.ResultType.SUCCESS,
      details = MessageToJson(instance.toGrpc())  # type: ignore[call-arg]
    )

  def _logFailureEvent(
      self, *,
      metadata: ObjectMetadata,
      action  : 'Event.Action.ActionType.V',
      details : str,
  ) -> None :
    """Log a CRUD failure event."""
    self._logEvent(
      target  = metadata.id,
      action  = action,
      result  = Event.Action.ResultType.ERROR,
      details = details,
    )

  def _logEvent(
      self, *,
      target : str,
      action : 'Event.Action.ActionType.V',
      result : 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log a CRUD event."""
    SINGLETON.structuredLogger.logEvent(
      target     = target,
      targetType = self.model.modelType(),
      owner      = self.khaleesiGetOwner(),
      action     = '',
      actionCrud = action,
      result     = result,
      details    = details,
    )

  def khaleesiGetOwner(self) -> User :
    """Get the owner of an instance."""
    user = User()
    user.type = User.UserType.SYSTEM
    user.id   = f'{khaleesiSettings["METADATA"]["GATE"]}-{khaleesiSettings["METADATA"]["SERVICE"]}'
    return user


class Model(BaseModel[Grpc], ABC, Generic[Grpc], metaclass = AbstractModelMeta):  # type: ignore[misc]  # pylint: disable=line-too-long
  """khaleesi.ninja base model which sends events upon changes."""

  objects = ModelManager()  # type: ignore[assignment]

  class Meta:
    abstract = True
