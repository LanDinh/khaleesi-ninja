"""Manager specific for migrations."""

# Python.
from typing import List

# Django.
from django.contrib.auth.models import Permission

# khaleesi.ninja.
from common.models.manager import Manager
from settings.settings import Settings
from .group_type import GroupType


class MigrationManager(Manager):
  """Provide the group creation methods necessary for migrations."""

  def update_or_create_anonymous(self, *, label: str, permissions: List[str]) -> None :
    """Update or create an anonymous group."""
    self._update_or_create_group(
        label = label,
        name = Settings.anonymous_suffix(),
        group_type = GroupType.ANONYMOUS,
        permissions = permissions,
    )

  def update_or_create_authenticated(self, *, label: str, permissions: List[str]) -> None :
    """Update or create an authenticated group."""
    self._update_or_create_group(
        label = label,
        name = Settings.authenticated_suffix(),
        group_type = GroupType.AUTHENTICATED,
        permissions = permissions,
    )

  def update_or_create_dragon(self, *, label: str, permissions: List[str]) -> None :
    """Update or create a dragon group."""
    self._update_or_create_group(
        label = label,
        name = Settings.dragon_suffix(),
        group_type = GroupType.DRAGON,
        permissions = permissions + [
            Settings.authenticated_suffix(),
            Settings.anonymous_suffix(),
        ],
    )

  def update_or_create_custom(self, *, label: str, name: str, permissions: List[str]) -> None :
    """Update or create a custom group."""
    self._update_or_create_group(
        label = label,
        name = name,
        group_type = GroupType.CUSTOM,
        permissions = permissions,
    )

  def _update_or_create_group(
      self, *,
      label: str,
      name: str,
      group_type: GroupType,
      permissions: List[str],
  ) -> None:
    """Update or create a group."""
    group, _ =  self._get_queryset().update_or_create(
        name = f'{label}.{name}',
        defaults = {'group_type': group_type}
    )
    group.permissions.set(Permission.objects.filter(
        codename__in = permissions,
        content_type__app_label = label,
    ))
