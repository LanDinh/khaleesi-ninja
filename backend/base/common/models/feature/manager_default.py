"""Default Manager."""

# Python.
from typing import cast

# khaleesi.ninja.
from common.exceptions import ZeroTupletException
from common.models.manager import Manager, T
from common.service_type import ServiceType


class DefaultManager(Manager):
  """Default Manager."""

  def get(self, *, service: ServiceType, name: str) -> T:
    """Get a feature."""
    return cast(T, super().get(service = service.name, name = name))

  def create(self, *, service: ServiceType, name: str) -> None :
    """Create a feature."""
    try:
      self.get(service = service, name = name)
    except ZeroTupletException:
      self.get_queryset().create(service = service.name, name = name)
