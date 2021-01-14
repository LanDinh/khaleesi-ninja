"""Default Manager."""

# Python.
from typing import Tuple

# khaleesi.ninja.
from common.models.auth.role.model import Role
from common.models.user.model import User
from common.models.manager import Manager, T


# noinspection PyTypeHints,SyntaxError
class DefaultManager(Manager[T]):
  """Default Manager."""

  def get_or_create(self, *, user: User, role: Role) -> Tuple[T, bool]:  # type: ignore[override]
    """Assign a role to a user."""
    return self.get_queryset().get_or_create(user = user, role = role)
