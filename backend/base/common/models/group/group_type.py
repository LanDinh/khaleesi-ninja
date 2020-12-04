"""The different types of groups."""

# Django.
from django.db import models


class GroupType(models.IntegerChoices):
  """The different types of groups that exist."""
  CUSTOM = 0  # pylint: disable=invalid-name
  ANONYMOUS = 1  # pylint: disable=invalid-name
  AUTHENTICATED = 2  # pylint: disable=invalid-name
  DRAGON = 3  # pylint: disable=invalid-name
