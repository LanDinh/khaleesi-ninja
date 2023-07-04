"""khaleesi.ninja base model."""

from __future__ import annotations

# Python.
from abc import ABC
from typing import Generic, TypeVar, Type
from uuid import uuid4

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.baseModel import (
  Grpc,
  Model as BaseModel,
  ModelManager as BaseModelManager,
  AbstractModelMeta
)
from khaleesi.proto.core_pb2 import ObjectMetadata


ModelType = TypeVar('ModelType', bound = 'Model')  # type: ignore[type-arg]  # pylint: disable=invalid-name


class ModelManager(BaseModelManager[ModelType], Generic[ModelType]):
  """Basic model manager for CRUD operations."""

  model: Type[ModelType]

  def baseKhaleesiGet(self, *, metadata: ObjectMetadata) -> ModelType :
    """Get an existing instance."""
    return self.get(khaleesiId = metadata.id)

  def khaleesiInstantiateNewInstance(self) -> ModelType :
    """Instantiate a new element."""
    instance= super().khaleesiInstantiateNewInstance()
    instance.khaleesiId = str(uuid4())
    return instance


class Model(BaseModel[Grpc], ABC, Generic[Grpc], metaclass = AbstractModelMeta):  # type: ignore[misc]  # pylint: disable=line-too-long
  """Basic model for gRPC conversions."""

  khaleesiId      = models.TextField(unique = True, editable = False)

  khaleesiCreated  = models.DateTimeField(auto_now_add = True)
  khaleesiModified = models.DateTimeField(auto_now = True)

  objects: ModelManager[Model[Grpc]] = ModelManager()  # type: ignore[assignment]

  def toGrpc(self, *, metadata: ObjectMetadata = ObjectMetadata(), grpc: Grpc) -> Grpc :
    """Return a grpc object containing own values."""
    grpc = super().toGrpc(metadata = metadata, grpc = grpc)
    metadata.id      = self.khaleesiId
    metadata.created.FromDatetime(self.khaleesiCreated)
    metadata.modified.FromDatetime(self.khaleesiModified)
    return grpc

  class Meta:
    abstract = True
