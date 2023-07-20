"""Test only models."""
from typing import Any

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import ObjectMetadata
from microservice.models.logs.abstract import Metadata as AbstractMetadata
from microservice.models.logs.metadataMixin import MetadataMixin, GrpcMetadataMixin
from microservice.models.logs.responseMetadataMixin import ResponseMetadataMixin


class OldMetadata(AbstractMetadata):
  """Allow instantiation of abstract model."""


class Metadata(MetadataMixin):
  """Allow instantiation of abstract model."""

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    return ObjectMetadata()


class GrpcMetadata(GrpcMetadataMixin):
  """Allow instantiation of abstract model."""

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    return ObjectMetadata()


class ResponseMetadata(ResponseMetadataMixin):
  """Allow instantiation of abstract model."""

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    return ObjectMetadata()

  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Any,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""

  def toGrpc(
      self, *,
      metadata: ObjectMetadata   = ObjectMetadata(),
      grpc    : Any,
  ) -> Any :
    """Return a grpc object containing own values."""
