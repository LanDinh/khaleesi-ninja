"""The different kinds of services."""

# pylint: disable=invalid-name

# Python.
from enum import Enum


class FeatureState(Enum):
  """The different kinds of services."""
  BETA = 'beta'  # only beta testers have access.
  RELEASED = 'released'  # everyone has access.
  LOCKED = 'locked'  # only superadmins have access.
