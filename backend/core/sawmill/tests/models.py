"""Test only models."""
from typing import Any

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import ObjectMetadata
from microservice.models.logs.metadataMixin import MetadataMixin, GrpcMetadataMixin
from microservice.models.logs.responseMetadataMixin import ResponseMetadataMixin


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


class ResponseMetadata(MetadataMixin, ResponseMetadataMixin):  # type: ignore[misc]
  """Allow instantiation of abstract model."""

  def khaleesiSave(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : Any,
      dbSave  : bool = True,
  ) -> None :
    """Change own values according to the grpc object."""

  def toGrpc(self) -> Any :
    """Return a grpc object containing own values."""

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    return ObjectMetadata()
