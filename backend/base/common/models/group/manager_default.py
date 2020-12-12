"""Default Manager."""

# Python.
from typing import cast, Optional

# khaleesi.ninja.
from ..manager import Manager, T


class DefaultManager(Manager):
  """Default Manager."""

  def get(self, *, name: str, label: Optional[str] = None) -> T :
    """Get a single group."""
    if label:
      return cast(T, super().get(name = f'{label}.{name}'))
    return cast(T, super().get(name = name))
