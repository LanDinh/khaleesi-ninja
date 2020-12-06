"""Custom base model to configure default managers."""

# Django.
from django.db import models

# khaleesi.ninja.
from common.models import Manager


class Model(models.Model):
  """Custom base model to configure default managers."""

  _objects = models.Manager()
  objects = Manager()

  class Meta:
    """Define the default manager."""
    abstract = True
    default_manager_name = '_objects'
