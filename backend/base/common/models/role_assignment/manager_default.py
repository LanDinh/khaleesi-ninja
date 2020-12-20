"""Default Manager."""

# Python.
from typing import Optional

# khaleesi.ninja.
from common.models.role.model import Role
from common.models.user.model import User
from common.models.manager import Manager


class DefaultManager(Manager):
  """Default Manager."""

  def create(self, *, user: User, role: Role, beta: Optional[bool] = False) -> None:
    """Assign a role to a user."""
    self._get_queryset().create(user = user, role = role, beta = beta)
