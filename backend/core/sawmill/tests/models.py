"""Test only models."""

# khaleesi.ninja.
from microservice.models.logs.abstract import Metadata as AbstractMetadata
from microservice.models.logs.abstractResponse import ResponseMetadata as AbstractResponseMetadata
from microservice.models.logs.metadataMixin import MetadataMixin, GrpcMetadataMixin


class OldMetadata(AbstractMetadata):
  """Allow instantiation of abstract model."""


class ResponseMetadata(AbstractResponseMetadata):
  """Allow instantiation of abstract model."""


class Metadata(MetadataMixin):
  """Allow instantiation of abstract model."""


class GrpcMetadata(GrpcMetadataMixin):
  """Allow instantiation of abstract model."""
