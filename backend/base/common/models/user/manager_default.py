"""Default Manager."""

# pylint: disable=line-too-long

# Python.
from typing import List

# khaleesi.ninja.
from common.models.auth.role.model import Role
from common.models.manager import  Manager, T
from settings.settings import UserNames


# noinspection PyTypeHints,PyUnresolvedReferences,SyntaxError,PyMissingOrEmptyDocstring
class DefaultManager(Manager[T]):
  """Default Manager."""

  def without_role_assignment(self, *, role: Role) -> List[T] :
    """Get all users without this role."""
    return list(
        self.get_queryset().exclude(roles = role).exclude(username = UserNames.anonymous()),
    )

  def create(self, *, username: str) -> T :  # type: ignore[override]
    """Create a new user."""
    user = self.model(username = self.model.normalize_username(username))  # type: ignore[attr-defined]
    user.set_unusable_password()  # type: ignore[attr-defined]
    user.full_clean()
    user.save()
    return user
