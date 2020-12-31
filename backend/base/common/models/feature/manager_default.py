"""Default Manager."""

# Python.
from typing import cast

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.service_type import ServiceType


class DefaultManager(Manager):
  """Default Manager."""

  def get_or_create(self, *, service: ServiceType, name: str) -> T :
    """Create a feature."""
    feature, _ = self.get_queryset().get_or_create(service = service.name, name = name)
    return cast(T, feature)
