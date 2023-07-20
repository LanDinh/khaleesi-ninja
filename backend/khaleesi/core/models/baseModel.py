"""khaleesi.ninja base model."""

from __future__ import annotations

# Python.
from typing import TypeVar, Generic, Any

# Django.
from django.db import models, transaction

# gRPC.
from google.protobuf.message import Message

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import DbOutdatedInformationException
from khaleesi.proto.core_pb2 import ObjectMetadata


Grpc = TypeVar('Grpc', bound = Message)


class Model(models.Model, Generic[Grpc]):
  """Basic model for gRPC conversions."""

  khaleesiVersion = models.IntegerField(default = 0)

  objects: models.Manager[Model]  # type: ignore[type-arg]

  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Grpc,  # pylint: disable=unused-argument
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    with transaction.atomic():
      oldVersion = self.khaleesiVersion
      if not self._state.adding:
        self.refresh_from_db()
      if not (oldVersion == self.khaleesiVersion and self.khaleesiVersion == metadata.version):
        raise DbOutdatedInformationException(objectType = self.modelType(), metadata = metadata)
      self.khaleesiVersion += 1
      self.save(*args, **kwargs)

  @classmethod
  def modelType(cls) -> str :
    """Model type for documentation purposes."""
    return f'{cls.__module__}.{cls.__qualname__}'

  def toGrpc(self, *, metadata: ObjectMetadata = ObjectMetadata(), grpc: Grpc) -> Grpc :
    """Return a grpc object containing own values."""
    metadata.version = self.khaleesiVersion
    return grpc

  class Meta:
    abstract = True
    ordering = [ 'pk' ]
