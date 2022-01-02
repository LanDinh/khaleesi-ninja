"""Test only models."""

# khaleesi.ninja.
from microservice.models.abstract import Metadata as AbstractMetadata


class Metadata(AbstractMetadata):
  """Allow instantiation of abstract model."""
