"""Features group views."""

# Python.
from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.auth.feature.feature_state import FeatureState
from common.models.auth.feature.manager_default import DefaultManager
from common.models.model import choices, Model
from common.service_type import ServiceType


class Feature(Model):
  """Features group views."""

  service = models.CharField(max_length = 50, choices = choices(ServiceType))
  name = models.CharField(max_length = 50)
  state = models.CharField(
      max_length = 50,
      choices = choices(FeatureState),
      default = FeatureState.BETA.name,
  )

  objects: DefaultManager[Feature] = DefaultManager()

  class Meta:
    """Feature meta attributes."""
    unique_together = ('service', 'name')
