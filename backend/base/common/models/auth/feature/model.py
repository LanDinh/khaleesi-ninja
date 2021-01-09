"""Features group views."""

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.auth.feature.manager_default import DefaultManager
from common.models.model import choices, Model
from common.service_type import ServiceType


class Feature(Model):
  """Features group views."""

  service = models.CharField(max_length = 50, choices = choices(ServiceType))
  name = models.CharField(max_length = 50, blank = True)

  objects = DefaultManager()
