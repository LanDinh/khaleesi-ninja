"""Test only models."""

from __future__ import annotations

# Python.
from abc import ABC
from typing import Any
from unittest.mock import MagicMock

# gRPC.
from google.protobuf.message import Message

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Model, ModelManager as BaseModelManager
from khaleesi.proto.core_pb2 import ObjectMetadata


class Grpc(Message, ABC):
  """Helper class."""


class ModelManager(BaseModelManager['BaseModel']):
  """Allow instantiation of abstract model."""

  def baseKhaleesiGet(self, *, metadata: ObjectMetadata) -> BaseModel :
    """Get an existing instance."""
    return self.model()


class BaseModel(Model[Grpc]):
  """Allow instantiation of abstract model."""

  saved  : bool
  objects: ModelManager = ModelManager()    # type: ignore[assignment]
  grpc = Grpc

  def __init__(self) -> None :
    """Initialize the instance."""
    super().__init__()
    self.saved = False

  def fromGrpc(self, *, grpc: Grpc) -> None :
    """Change own values according to the grpc object."""

  def toGrpc(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Grpc           = MagicMock(),
  ) -> Grpc :
    """Return a grpc object containing own values."""
    return super().toGrpc(metadata = metadata, grpc = grpc)

  def save(self, *args: Any, **kwargs: Any) -> None :
    """Don't talk to the database."""
    self.saved = True
