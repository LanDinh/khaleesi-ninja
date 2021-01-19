"""Manager specific for migrations."""

# pylint: disable=line-too-long

# Python.
from typing import Optional

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.service_type import ServiceType


# noinspection PyTypeHints,SyntaxError
class MigrationManager(Manager[T]):
  """Provide the creation methods necessary for migrations."""

  def create(self, *, service: ServiceType, name: Optional[str] = '') -> None:  # type: ignore[override]
    """Create a role."""
    self.get_queryset().get_or_create(service = service.name, name = name)
