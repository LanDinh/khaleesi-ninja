"""Add custom attributes to groups."""

# Django.
from django.contrib.auth.models import Group as DjangoGroup
from django.db import models

# khaleesi.ninja.
from common.models.group.group_type import GroupType
from common.models.group.manager_default import DefaultManager
from common.models.group.manager_migrations import MigrationManager
from common.models.model import Model


class Group(Model, DjangoGroup):
  """Add custom attributes to groups."""
  # The type of group at hand.
  group_type = models.IntegerField(choices = GroupType.choices, default = GroupType.CUSTOM)

  objects = DefaultManager()
  migrations = MigrationManager()
