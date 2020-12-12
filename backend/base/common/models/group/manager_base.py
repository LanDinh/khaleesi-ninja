"""Manager specific for migrations."""

# khaleesi.ninja.
from common.models.manager import Manager


class BaseManager(Manager):
  """Provide the group creation methods necessary for migrations."""

  def create_group(self, *, label: str, name: str) -> None:
    """Update or create a group."""
    self._get_queryset().update_or_create(name = f'{label}.{name}')
