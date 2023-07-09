"""khaleesi.ninja base model which sends events upon changes."""

from __future__ import annotations

# Python.
from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

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
from .baseModel import Grpc, AbstractModelMeta
from .idModel import Model as BaseModel, ModelManager as BaseModelManager


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


ModelType = TypeVar('ModelType', bound = 'Model')  # type: ignore[type-arg]  # pylint: disable=invalid-name

class ModelManager(BaseModelManager[ModelType], Generic[ModelType]):
  """khaleesi.ninja base model manager which sends events upon changes."""

  model: Type[ModelType]

  def khaleesiCreate(self, *, grpc: Grpc) -> ModelType :
    """Create a new instance."""
    try:
      instance = super().khaleesiCreate(grpc = grpc)
      self._logSuccessEvent(
        instance = instance,
        action   = Event.Action.ActionType.CREATE,
        details  = MessageToJson(grpc),
      )
      return instance
    except Exception:
      self._logFailureEvent(
        metadata = ObjectMetadata(),
        grpc     = grpc,
        action   = Event.Action.ActionType.CREATE,
        details  = MessageToJson(grpc),
      )
      raise

  def khaleesiUpdate(self, *, metadata: ObjectMetadata, grpc: Grpc) -> ModelType :
    """Update an existing instance."""
    try:
      instance = super().khaleesiUpdate(metadata = metadata, grpc = grpc)
      self._logSuccessEvent(
        instance = instance,
        action   = Event.Action.ActionType.UPDATE,
        details  = MessageToJson(metadata) + '\n' + MessageToJson(grpc),
      )
      return instance
    except Exception:
      self._logFailureEvent(
        metadata = metadata,
        grpc     = grpc,
        action   = Event.Action.ActionType.UPDATE,
        details  = MessageToJson(metadata) + '\n' + MessageToJson(grpc),
      )
      raise

  def khaleesiDelete(self, *, metadata: ObjectMetadata) -> ModelType :
    """Delete an existing instance."""
    try:
      instance = super().khaleesiDelete(metadata = metadata)
      self._logSuccessEvent(
        instance = instance,
        action   = Event.Action.ActionType.DELETE,
        details  = MessageToJson(metadata),
      )
      return instance
    except Exception:
      self._logFailureEvent(
        metadata = metadata,
        grpc     = self.model.grpc(),
        action   = Event.Action.ActionType.DELETE,
        details  = MessageToJson(metadata),
      )
      raise


  def _logSuccessEvent(
      self, *,
      instance: Model[Grpc],
      action  : 'Event.Action.ActionType.V',
      details : str,
  ) -> None :
    """Log a CRUD success event."""
    self._logEvent(
      owner   = instance.getKhaleesiOwner(),
      target  = instance.khaleesiId,
      action  = action,
      result  = Event.Action.ResultType.SUCCESS,
      details = details,
    )

  def _logFailureEvent(
      self, *,
      metadata: ObjectMetadata,
      grpc    : Grpc,
      action  : 'Event.Action.ActionType.V',
      details : str,
  ) -> None :
    """Log a CRUD failure event."""
    self._logEvent(
      owner   = self.model.getDefaultKhaleesiOwner(metadata = metadata, grpc = grpc),  # type: ignore[arg-type]  # pylint: disable=line-too-long
      target  = metadata.id,
      action  = action,
      result  = Event.Action.ResultType.ERROR,
      details = details,
    )

  def _logEvent(
      self, *,
      owner  : User,
      target : str,
      action : 'Event.Action.ActionType.V',
      result : 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log a CRUD event."""
    event = Event()
    event.target.id = target
    event.target.type = self.model.modelType()
    event.target.owner.CopyFrom(owner)
    event.action.crudType = action
    event.action.result = result
    event.action.details = details
    SINGLETON.structuredLogger.logEvent(event = event)


class Model(BaseModel[Grpc], ABC, Generic[Grpc], metaclass = AbstractModelMeta):  # type: ignore[misc]  # pylint: disable=line-too-long
  """khaleesi.ninja base model which sends events upon changes."""

  khaleesiCreated        = models.DateTimeField(auto_now_add = True)
  khaleesiCreatedById    = models.TextField()
  khaleesiCreatedByType  = models.TextField()
  khaleesiModified       = models.DateTimeField(auto_now = True)
  khaleesiModifiedById   = models.TextField()
  khaleesiModifiedByType = models.TextField()

  objects: ModelManager[Model[Grpc]] = ModelManager()  # type: ignore[assignment]

  @staticmethod
  def getDefaultKhaleesiOwner(*, metadata: ObjectMetadata, grpc: Grpc) -> User :  # pylint: disable=unused-argument
    """Get the default owner if there is no instance."""
    user = User()
    user.type = User.UserType.SYSTEM
    user.id   = f'{khaleesiSettings["METADATA"]["GATE"]}-{khaleesiSettings["METADATA"]["SERVICE"]}'
    return user


  def getKhaleesiOwner(self) -> User :
    """Get the owner of an instance."""
    user = User()
    user.type = User.UserType.SYSTEM
    user.id   = f'{khaleesiSettings["METADATA"]["GATE"]}-{khaleesiSettings["METADATA"]["SERVICE"]}'
    return user

  @abstractmethod
  def fromGrpc(self, *, grpc: Grpc) -> None :
    """Set modification metadata from gRPC."""
    super().fromGrpc(grpc = grpc)

    # Creation.
    if not self.pk:
      self.khaleesiCreatedById   = STATE.request.user.id
      self.khaleesiCreatedByType = User.UserType.Name(STATE.request.user.type)

    # Modification.
    self.khaleesiModifiedById   = STATE.request.user.id
    self.khaleesiModifiedByType = User.UserType.Name(STATE.request.user.type)

  @abstractmethod
  def toGrpc(self, *, metadata: ObjectMetadata, grpc: Grpc) -> Grpc :
    """Return a grpc object containing own values."""
    grpc = super().toGrpc(metadata = metadata, grpc = grpc)
    metadata.created.FromDatetime(self.khaleesiCreated)
    metadata.createdBy.id   = self.khaleesiCreatedById
    metadata.createdBy.type = User.UserType.Value(self.khaleesiCreatedByType)
    metadata.modified.FromDatetime(self.khaleesiModified)
    metadata.modifiedBy.id   = self.khaleesiModifiedById
    metadata.modifiedBy.type = User.UserType.Value(self.khaleesiModifiedByType)
    return grpc

  class Meta(BaseModel.Meta):
    abstract = True
