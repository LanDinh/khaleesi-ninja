"""Test only models."""

from __future__ import annotations

# Python.
from unittest.mock import MagicMock

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.eventIdModelOwnedBySystem import Model as BaseModel
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models.baseModel import Grpc


class EventSystemModel(BaseModel[Grpc]):
  """Allow instantiation of abstract model."""

  objects: models.Manager[EventSystemModel]

  def toGrpc(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Grpc           = MagicMock(),
  ) -> Grpc :
    """Return a grpc object containing own values."""
    return super().toGrpc(metadata = metadata, grpc = grpc)
