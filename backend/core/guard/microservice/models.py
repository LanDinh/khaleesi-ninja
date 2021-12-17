"""core-guard models."""

from django.db import models


class TestModel(models.Model):
  """Test model."""
  text = models.CharField(max_length = 200)
