"""khaleesi.ninja base model."""

from __future__ import annotations

# Python.
from abc import ABC, ABCMeta, abstractmethod
from typing import TypeVar, Generic, Type

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# Django.
from django.db import models, transaction

# gRPC.
from google.protobuf.message import Message

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import (
  DbObjectNotFoundException,
  DbOutdatedInformationException,
  DbObjectTwinException,
)
from khaleesi.proto.core_pb2 import ObjectMetadata


Grpc      = TypeVar('Grpc', bound = Message)
ModelType = TypeVar('ModelType', bound = 'Model')  # type: ignore[type-arg]  # pylint: disable=invalid-name

class AbstractModelMeta(ABCMeta, type(models.Model)):  # type: ignore[misc]
  """Need this to circumvent metaclass conflicts."""


class ModelManager(models.Manager[ModelType], Generic[ModelType]):
  """Basic model manager for CRUD operations."""

  model: Type[ModelType]

  def khaleesiCreate(self, *, grpc: Grpc) -> ModelType :
    """Create a new instance."""
    return self._khaleesiEdit(
      instance = self.model(),
      grpc     = grpc,
      metadata = ObjectMetadata(),
    )

  def khaleesiUpdate(self, *, metadata: ObjectMetadata, grpc: Grpc) -> ModelType :
    """Update an existing instance."""
    with transaction.atomic(using = 'write'):
      return self._khaleesiEdit(
        instance = self.khaleesiGet(metadata = metadata),
        grpc     = grpc,
        metadata = metadata,
      )

  def khaleesiDelete(self, *, metadata: ObjectMetadata) -> ModelType :
    """Delete an existing instance."""
    with transaction.atomic(using = 'write'):
      instance = self.khaleesiGet(metadata = metadata)
      instance.delete()
      return instance

  def khaleesiGet(self, *, metadata: ObjectMetadata) -> ModelType :
    """Get an existing instance."""
    try:
      return self.baseKhaleesiGet(metadata = metadata)
    except ObjectDoesNotExist as exception:
      raise DbObjectNotFoundException(objectType = self.model.modelType()) from exception
    except MultipleObjectsReturned as exception:
      raise DbObjectTwinException(
        objectType = self.model.modelType(),
        objectId = metadata.id,
      ) from exception


  @abstractmethod
  def baseKhaleesiGet(self, *, metadata: ObjectMetadata) -> ModelType :
    """Define the basic get by metadata."""

  def _khaleesiEdit(
      self, *,
      instance: ModelType,
      grpc    : Grpc,
      metadata: ObjectMetadata,
  ) -> ModelType :
    if not instance.khaleesiVersion == metadata.version:
      raise DbOutdatedInformationException(objectType = self.model.modelType(), metadata = metadata)
    instance.fromGrpc(grpc = grpc)
    instance.khaleesiVersion += 1
    instance.save()
    return instance


class Model(models.Model, ABC, Generic[Grpc], metaclass = AbstractModelMeta):  # type: ignore[misc]
  """Basic model for gRPC conversions."""
  khaleesiVersion = models.IntegerField(default = 0)

  objects: ModelManager[Model[Grpc]]
  grpc   : Type[Grpc]

  @classmethod
  def modelType(cls) -> str :
    """Model type for documentation purposes."""
    return f'{cls.__module__}.{cls.__qualname__}'

  @abstractmethod
  def fromGrpc(self, *, grpc: Grpc) -> None :
    """Change own values according to the grpc object."""

  @abstractmethod
  def toGrpc(self, *, metadata: ObjectMetadata, grpc: Grpc) -> Grpc :
    """Return a grpc object containing own values."""
    metadata.version = self.khaleesiVersion
    return grpc

  class Meta:
    abstract = True
    ordering = [ 'pk' ]
