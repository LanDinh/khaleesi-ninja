"""The different kinds of services."""

# pylint: disable=invalid-name

# Python.
from enum import Enum


class FeatureAssignmentState(Enum):
  """The different kinds of services."""
  ALPHA = 'alpha'  # only superadmins have access.
  BETA = 'beta'  # only beta testers have access.
  RELEASED = 'released'  # everyone has access.
