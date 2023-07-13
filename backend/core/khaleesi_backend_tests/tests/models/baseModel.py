"""Test only models."""

from __future__ import annotations

# Python.
from abc import ABC
from unittest.mock import MagicMock

# gRPC.
from google.protobuf.message import Message

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Model
from khaleesi.proto.core_pb2 import ObjectMetadata


class Grpc(Message, ABC):
  """Helper class."""


class BaseModel(Model[Grpc]):
  """Allow instantiation of abstract model."""

  def toGrpc(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Grpc           = MagicMock(),
  ) -> Grpc :
    """Return a grpc object containing own values."""
    return super().toGrpc(metadata = metadata, grpc = grpc)
