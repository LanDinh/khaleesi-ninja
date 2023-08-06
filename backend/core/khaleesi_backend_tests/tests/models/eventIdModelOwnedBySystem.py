"""Test only models."""

from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.eventIdModelOwnedBySystem import Model as BaseModel
from tests.models.baseModel import Grpc


class EventSystemModel(BaseModel[Grpc]):
  """Allow instantiation of abstract model."""

  objects: models.Manager[EventSystemModel]
