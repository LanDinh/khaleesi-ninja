"""Add custom attributes to groups."""

# Django.
from django.contrib.auth.models import Group as DjangoGroup
from django.db import models

# khaleesi.ninja.
from .group_type import GroupType
from .manager_default import DefaultManager
from .manager_migrations import MigrationManager


class Group(DjangoGroup):
  """Add custom attributes to groups."""
  # The type of group at hand.
  group_type = models.IntegerField(choices = GroupType.choices, default = GroupType.CUSTOM)

  objects = DefaultManager()
  migrations = MigrationManager()
