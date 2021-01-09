"""Default Manager."""

# khaleesi.ninja.
from common.models.auth.feature.model import Feature
from common.models.auth.role.model import Role
from common.models.manager import Manager


class DefaultManager(Manager):
  """Default Manager."""

  def create(self, *, role: Role, feature: Feature) -> None:
    """Assign a role to a user."""
    self.get_queryset().create(role = role, feature = feature)
