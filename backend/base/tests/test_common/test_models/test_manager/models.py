"""Test models."""

# Django.
from django.db import models

# khaleesi.ninja
from common.models import Model


class TestModel(Model):
  """Test model holding the custom manager."""

  class TestMeta:
    """Detect test metadata."""
    testing = True


class TestRelation(Model):
  """Test model for testing related managers."""

  one_to_one = models.OneToOneField(
      TestModel,
      on_delete = models.CASCADE,
      related_name = 'one_to_one',
      blank =  True,
      null = True,
  )
  one_to_many = models.ForeignKey(
      TestModel,
      on_delete = models.CASCADE,
      related_name = 'one_to_many',
      blank =  True,
      null = True,
  )
  many_to_many = models.ManyToManyField(
      TestModel,
      related_name = 'many_to_many',
      blank =  True,
      null = True,
  )

  class TestMeta:
    """Detect test metadata."""
    testing = True
