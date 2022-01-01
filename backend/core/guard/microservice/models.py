"""core-guard models."""

# Django.
from django.db import models


class TestModel(models.Model):
  """Test model."""
  text = models.CharField(max_length = 200)

  objects = models.Manager()
