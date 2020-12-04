"""Default Manager."""

# Python.
from typing import cast

# khaleesi.ninja.
from ..manager import Manager, T


class DefaultManager(Manager):
  """Default Manager."""

  def get(self, *, label: str, name: str) -> T :
    """Get a single group."""
    return cast(T, super().get(name = f'{label}.{name}'))
