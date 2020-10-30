"""Test models."""

# Django.
from django.db import models

# khaleesi.ninja
from common.models import Manager


class TestModel(models.Model):
  """Test model holding the custom manager."""

  objects = Manager()

  class TestMeta:
    """Detect test metadata."""
    testing = True
