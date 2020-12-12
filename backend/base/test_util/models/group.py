"""Test utils for the Group model."""

# Python.
from typing import cast
from unittest.mock import MagicMock

# khaleesi.ninja.
from common.models import Group


class TestGroupUnitMixin:
  """Provide custom creations KhaleesiGroup tests."""

  @staticmethod
  def create_unit_group() -> Group :
    """Create a group usable for unit tests."""
    group = MagicMock()
    group.save = MagicMock()
    group.user_set = MagicMock()
    group.permissions = MagicMock()
    group.permissions.set = MagicMock()
    return cast(Group, group)
