"""Role assignment attributes."""

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.feature.model import Feature
from common.models.feature_assignment.feature_assignment_state import (
  FeatureAssignmentState
)
from common.models.role.model import Role
from common.models.model import choices, Model
from common.models.feature_assignment.manager_default import DefaultManager


class FeatureAssignment(Model):
  """Role assignment attributes."""

  role = models.ForeignKey(Role, on_delete = models.CASCADE)
  feature = models.ForeignKey(Feature, on_delete = models.CASCADE)
  state = models.CharField(
      max_length = 50,
      choices = choices(FeatureAssignmentState),
      default = FeatureAssignmentState.ALPHA.name,
  )

  objects = DefaultManager()

  class Meta:
    """Role meta attributes."""
    unique_together = ('role', 'feature')
