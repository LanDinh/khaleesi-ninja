"""Default Manager."""

# pylint: disable=line-too-long

# Python.
from typing import Tuple

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.service_type import ServiceType


# noinspection PyTypeHints,SyntaxError
class DefaultManager(Manager[T]):
  """Default Manager."""

  def get_or_create(self, *, service: ServiceType, name: str) -> Tuple[T, bool] :  # type: ignore[override]
    """Create a feature."""
    return self.get_queryset().get_or_create(service = service.name, name = name)
