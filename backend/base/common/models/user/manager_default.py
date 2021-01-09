"""Default Manager."""

# Python.
from typing import cast, List

# khaleesi.ninja.
from common.models.auth.role.model import Role
from common.models.manager import  Manager, T
from settings.settings import UserNames


class DefaultManager(Manager):
  """Default Manager."""

  def without_role_assignment(self, *, role: Role) -> List[T] :
    """Get all users without this role."""
    return list(
        self.get_queryset().exclude(roles = role).exclude(username = UserNames.anonymous()),
    )

  def create(self, *, username: str) -> T :
    """Create a new user."""
    user = self.model(username = self.model.normalize_username(username))
    user.set_unusable_password()
    user.full_clean()
    user.save()
    return cast(T, user)
