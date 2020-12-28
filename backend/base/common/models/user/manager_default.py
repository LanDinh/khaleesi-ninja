"""Default Manager."""

# Python.
from typing import cast, Optional, List

# khaleesi.ninja.
from common.models.role.model import Role
from common.models.manager import  Manager, T
from settings.settings import UserNames


class DefaultManager(Manager):
  """Default Manager."""

  def get(self, *, username: str) -> T :
    """Get a single user by name."""
    return cast(T, super().get(username = username))

  def without_role_assignment(self, *, role: Role) -> List[T] :
    """Get all users without this role."""
    return list(
        self.get_queryset().exclude(roles = role).exclude(username = UserNames.anonymous()),
    )

  def create(self, *, username: str, password: Optional[str] = None) -> T :
    """Create a new user."""
    user = self.model(username = self.model.normalize_username(username))
    if password is None:
      user.set_unusable_password()
    else:
      user.set_password(raw_password = password)
    user.full_clean()
    user.save()
    return cast(T, user)
