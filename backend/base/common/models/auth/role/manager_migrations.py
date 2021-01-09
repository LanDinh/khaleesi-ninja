"""Manager specific for migrations."""

# Python.
from typing import Optional

# khaleesi.ninja.
from common.models.manager import Manager
from common.service_type import ServiceType


class MigrationManager(Manager):
  """Provide the creation methods necessary for migrations."""

  def create(self, *, service: ServiceType, name: Optional[str] = '') -> None:
    """Create a role."""
    self.get_queryset().update_or_create(service = service.name, name = name)
