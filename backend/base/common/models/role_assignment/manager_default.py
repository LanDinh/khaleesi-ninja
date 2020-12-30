"""Default Manager."""

# khaleesi.ninja.
from common.models.role.model import Role
from common.models.user.model import User
from common.models.manager import Manager


class DefaultManager(Manager):
  """Default Manager."""

  def get_or_create(self, *, user: User, role: Role) -> None:
    """Assign a role to a user."""
    self.get_queryset().get_or_create(user = user, role = role)
