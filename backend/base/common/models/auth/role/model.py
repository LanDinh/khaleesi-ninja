"""User roles for authorization."""

# Python.
from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.auth.feature.model import Feature
from common.models.auth.role.manager_default import DefaultManager
from common.models.auth.role.manager_migrations import MigrationManager
from common.models.model import choices, Model
from common.service_type import ServiceType


class Role(Model):
  """Add custom attributes to roles."""

  service = models.CharField(max_length = 50, choices = choices(ServiceType))
  name = models.CharField(max_length = 50, blank = True)
  authenticated = models.BooleanField(default = False)
  features = models.ManyToManyField(Feature, through = 'FeatureAssignment', related_name = 'roles')

  objects: DefaultManager[Role] = DefaultManager()
  migrations: MigrationManager[Role] = MigrationManager()

  class Meta:
    """Role meta attributes."""
    unique_together = ('service', 'name')
