"""Add custom attributes to groups."""

# Django.
from django.contrib.auth.models import Group as DjangoGroup
from django.db import models

# khaleesi.ninja.
from common.models.group.manager_default import DefaultManager
from common.models.group.manager_base import BaseManager
from common.models.model import Model


class Group(Model, DjangoGroup):
  """Add custom attributes to groups."""
  # All authenticated users get automatically added to this group.
  authenticated = models.BooleanField(default = False)
  # All beta testers get automatically added to this group.
  beta = models.BooleanField(default = False)
  # All translators get automatically added to this group.
  translator = models.BooleanField(default = False)

  objects = DefaultManager()
  base = BaseManager()
