"""Test only models."""

from __future__ import annotations

# Python.
from abc import ABC

# Django.
from django.db import models

# gRPC.
from google.protobuf.message import Message

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Model


class Grpc(Message, ABC):
  """Helper class."""


class BaseModel(Model[Grpc]):
  """Allow instantiation of abstract model."""

  objects: models.Manager[BaseModel]
