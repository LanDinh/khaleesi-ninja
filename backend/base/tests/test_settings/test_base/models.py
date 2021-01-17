"""Test models."""

# khaleesi.ninja
from django.db import models

from common.models import Model


class TestModel(Model):
  """Test model holding the custom manager."""

  name = models.CharField(max_length = 10)

  class TestMeta:
    """Detect test metadata."""
    testing = True
