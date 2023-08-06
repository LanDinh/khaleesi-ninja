"""Test only models."""

from __future__ import annotations

# Python.
from abc import ABC

# gRPC.
from google.protobuf.message import Message

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Model, Manager


class Grpc(Message, ABC):
  """Helper class."""


class BaseModel(Model[Grpc]):
  """Allow instantiation of abstract model."""

  objects: Manager[BaseModel]  # type: ignore[assignment]
