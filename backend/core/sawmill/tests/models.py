"""Test only models."""

# khaleesi.ninja.
from microservice.models.logs.abstract import Metadata as AbstractMetadata
from microservice.models.logs.abstract_response import ResponseMetadata as AbstractResponseMetadata


class Metadata(AbstractMetadata):
  """Allow instantiation of abstract model."""


class ResponseMetadata(AbstractResponseMetadata):
  """Allow instantiation of abstract model."""
