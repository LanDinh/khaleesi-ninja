"""Test models."""

# khaleesi.ninja
from common.models import Model


class TestModel(Model):
  """Test model holding the custom manager."""

  class TestMeta:
    """Detect test metadata."""
    testing = True
