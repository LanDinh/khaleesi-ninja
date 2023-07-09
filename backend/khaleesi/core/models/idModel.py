"""khaleesi.ninja base model."""

from __future__ import annotations

# Python.
from abc import ABC, abstractmethod
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


class Model(BaseModel[Grpc], ABC, Generic[Grpc], metaclass = AbstractModelMeta):  # type: ignore[misc]  # pylint: disable=line-too-long
  """Basic model for gRPC conversions."""

  khaleesiId      = models.TextField(unique = True, editable = False)

  objects: ModelManager[Model[Grpc]] = ModelManager()  # type: ignore[assignment]

  @abstractmethod
  def fromGrpc(self, *, grpc: Grpc) -> None :
    """Set modification metadata from gRPC."""
    if not self.pk:
      self.khaleesiId = str(uuid4())

  @abstractmethod
  def toGrpc(self, *, metadata: ObjectMetadata, grpc: Grpc) -> Grpc :
    """Return a grpc object containing own values."""
    grpc = super().toGrpc(metadata = metadata, grpc = grpc)
    metadata.id = self.khaleesiId
    return grpc

  class Meta(BaseModel.Meta):
    abstract = True
