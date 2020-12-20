"""User roles for authorization."""

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.role.manager_default import DefaultManager
from common.models.role.manager_migrations import MigrationManager
from common.models.model import choices, Model
from common.service_type import ServiceType


class Role(Model):
  """Add custom attributes to roles."""

  service = models.CharField(max_length = 50, choices = choices(ServiceType))
  name = models.CharField(max_length = 50, blank = True)
  authenticated = models.BooleanField(default = False)

  objects = DefaultManager()
  migrations = MigrationManager()

  class Meta:
    """Role meta attributes."""
    unique_together = ('service', 'name')
