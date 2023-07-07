"""Test only models."""

from __future__ import annotations

# Python.
from typing import Any
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.models.eventSystemModel import Model as BaseModel, ModelManager
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models.baseModel import Grpc


class EventSystemModel(BaseModel[Grpc]):
  """Allow instantiation of abstract model."""

  objects: ModelManager[EventSystemModel]  # type: ignore[assignment]
  grpc = Grpc

  def fromGrpc(self, *, grpc: Grpc) -> None :  # pylint: disable=useless-super-delegation
    """Change own values according to the grpc object."""
    super().fromGrpc(grpc = grpc)

  def toGrpc(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Grpc           = MagicMock(),
  ) -> Grpc :
    """Return a grpc object containing own values."""
    return super().toGrpc(metadata = metadata, grpc = grpc)

  def save(self, *args: Any, **kwargs: Any) -> None :
    """Don't talk to the database."""
