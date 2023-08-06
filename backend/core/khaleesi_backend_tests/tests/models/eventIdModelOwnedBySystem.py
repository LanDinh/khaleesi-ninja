"""Test only models."""

from __future__ import annotations

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Manager
from khaleesi.core.models.eventIdModelOwnedBySystem import Model as BaseModel
from tests.models.baseModel import Grpc


class EventSystemModel(BaseModel[Grpc]):
  """Allow instantiation of abstract model."""

  objects: Manager[EventSystemModel]  # type: ignore[assignment]
