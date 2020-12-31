"""Default Manager."""

# Python.
from typing import List

# khaleesi.ninja.
from common.models.manager import Manager, T


class DefaultManager(Manager):
  """Default Manager."""

  def authenticated(self) -> List[T] :
    """Get all roles that all authenticated users should get assigned."""
    return list(self.get_queryset().filter(authenticated = True))
