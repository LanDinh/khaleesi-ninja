"""Default Manager."""

# Python.
from typing import Optional, cast

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.service_type import ServiceType


class DefaultManager(Manager):
  """Default Manager."""

  def get(self, *, service: ServiceType, name: Optional[str] = '') -> T:
    """Get a role."""
    return cast(T, super().get(service = service.name, name = name))
