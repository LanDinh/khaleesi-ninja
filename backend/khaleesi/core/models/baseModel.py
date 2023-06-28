"""khaleesi.ninja base model."""

from __future__ import annotations

# Python.
from abc import ABC, ABCMeta, abstractmethod
from typing import TypeVar, Generic
from uuid import uuid4

# Django.
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction

# gRPC.
from google.protobuf.message import Message

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import (
  DbOutdatedInformationException,
  DbObjectNotFoundException,
)
from khaleesi.proto.core_pb2 import ObjectMetadata


Grpc = TypeVar('Grpc', bound = Message)

class AbstractModelMeta(ABCMeta, type(models.Model)):  # type: ignore[misc]
  """Need this to circumvent metaclass conflicts."""


class ModelManager(models.Manager['Model'], Generic[Grpc]):  # type: ignore[type-arg]
  """Basic model manager for CRUD operations."""

  def khaleesiCreate(self, *, grpc: Grpc) -> 'Model'[Grpc] :  # pylint: disable=invalid-sequence-index
    """Create a new instance."""
    instance = self.model()
    instance.khaleesiId = str(uuid4())
    return self._khaleesiEdit(instance = instance, grpc = grpc, metadata = ObjectMetadata())

  def khaleesiUpdate(self, *, metadata: ObjectMetadata, grpc: Grpc) -> 'Model'[Grpc] :  # pylint: disable=invalid-sequence-index
    """Update an existing instance."""
    with transaction.atomic(using = 'write'):
      return self._khaleesiEdit(
        instance = self.khaleesiGet(metadata = metadata),
        grpc     = grpc,
        metadata = metadata,
      )

  def khaleesiDelete(self, *, metadata: ObjectMetadata) -> None :
    """Delete an existing instance."""
    self.filter(khaleesiId = metadata.id).delete()

  def khaleesiGet(self, *, metadata: ObjectMetadata) -> 'Model'[Grpc] :  # pylint: disable=invalid-sequence-index
    """Get an existing instance."""
    try:
      return self.get(khaleesiId = metadata.id)
    except ObjectDoesNotExist as exception:
      raise DbObjectNotFoundException(objectType = self.model.modelType()) from exception

  def _khaleesiEdit(
      self, *,
      instance: 'Model'[Grpc],  # pylint: disable=invalid-sequence-index
      grpc    : Grpc,
      metadata: ObjectMetadata,
  ) -> 'Model'[Grpc] :  # pylint: disable=invalid-sequence-index
    if not instance.khaleesiVersion == metadata.version:
      raise DbOutdatedInformationException(objectType = self.model.modelType(), metadata = metadata)
    instance.fromGrpc(grpc = grpc)
    instance.khaleesiVersion += 1
    instance.save()
    return instance


class Model(models.Model, ABC, Generic[Grpc], metaclass = AbstractModelMeta):  # type: ignore[misc]
  """Basic model for gRPC conversions."""

  khaleesiId      = models.TextField(unique = True, editable = False)
  khaleesiVersion = models.IntegerField(default = 0)

  khaleesiCreated  = models.DateTimeField(auto_now_add = True)
  khaleesiModified = models.DateTimeField(auto_now = True)

  objects = ModelManager()

  @classmethod
  def modelType(cls) -> str :
    """Model type for documentation purposes."""
    return f'{cls.__module__}.{cls.__qualname__}'

  @abstractmethod
  def fromGrpc(self, *, grpc: Grpc) -> None :
    """Change own values according to the grpc object."""

  def toGrpc(self, *, metadata: ObjectMetadata = ObjectMetadata(), grpc: Grpc) -> Grpc :
    """Return a grpc object containing own values."""
    metadata.id      = self.khaleesiId
    metadata.version = self.khaleesiVersion
    metadata.created.FromDatetime(self.khaleesiCreated)
    metadata.modified.FromDatetime(self.khaleesiModified)
    return grpc

  class Meta:
    abstract = True
