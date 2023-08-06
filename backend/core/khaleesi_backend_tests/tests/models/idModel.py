"""Test only models."""

from __future__ import annotations

# Python.

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.idModel import Model as BaseModel
from tests.models.baseModel import Grpc


class IdModel(BaseModel[Grpc]):
  """Allow instantiation of abstract model."""

  objects: models.Manager[IdModel]
