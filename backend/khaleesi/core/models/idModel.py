"""khaleesi.ninja base model."""

from __future__ import annotations

# Python.
from typing import Generic, Any
from uuid import uuid4

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import ObjectMetadata
from .baseModel import Grpc, Model as BaseModel, Manager


class Model(BaseModel[Grpc], Generic[Grpc]):
  """Basic model for gRPC conversions."""

  khaleesiId = models.TextField(unique = True, editable = False)

  objects: Manager[Model]  # type: ignore[type-arg,assignment]

  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Grpc,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    if self._state.adding:
      self.khaleesiId = str(uuid4())
    super().khaleesiSave(*args, metadata = metadata, grpc = grpc, **kwargs)

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    metadata = super().toObjectMetadata()
    metadata.id = self.khaleesiId
    return metadata

  class Meta(BaseModel.Meta):
    abstract = True
