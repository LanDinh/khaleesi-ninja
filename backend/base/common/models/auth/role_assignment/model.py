"""Role assignment attributes."""

# Python.
from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.auth.role.model import Role
from common.models.model import Model
from common.models.auth.role_assignment.manager_default import DefaultManager
from common.models.user.model import User


class RoleAssignment(Model):
  """Role assignment attributes."""

  user = models.ForeignKey(User, on_delete = models.CASCADE)
  role = models.ForeignKey(Role, on_delete = models.CASCADE)
  beta = models.BooleanField(default = False)

  objects: DefaultManager[RoleAssignment] = DefaultManager()

  class Meta:
    """Role meta attributes."""
    unique_together = ('user', 'role')
