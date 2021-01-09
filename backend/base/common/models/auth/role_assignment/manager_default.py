"""Default Manager."""

# Python.
from typing import cast

# khaleesi.ninja.
from common.models.auth.role.model import Role
from common.models.user.model import User
from common.models.manager import Manager, T


class DefaultManager(Manager):
  """Default Manager."""

  def get_or_create(self, *, user: User, role: Role) -> T:
    """Assign a role to a user."""
    assignment, _ = self.get_queryset().get_or_create(user = user, role = role)
    return cast(T, assignment)
