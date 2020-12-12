"""Manager specific for migrations."""

# khaleesi.ninja.
from common.models.manager import Manager


class MigrationManager(Manager):
  """Provide the group creation methods necessary for migrations."""

  def create(self, *, name: str) -> None:
    """Update or create a group."""
    self._get_queryset().update_or_create(name = name)
