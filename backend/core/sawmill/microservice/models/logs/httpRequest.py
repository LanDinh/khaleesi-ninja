"""Request logs."""

# pylint:disable=duplicate-code

# Python.
from __future__ import annotations
from typing import List, Any

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Model
from khaleesi.proto.core_pb2 import ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import HttpRequestRequest as GrpcHttpRequest
from microservice.models.logs.metadataMixin import MetadataMixin
from microservice.models.logs.responseMetadataMixin import ResponseMetadataMixin


class HttpRequest(Model[GrpcHttpRequest], MetadataMixin, ResponseMetadataMixin):  # type: ignore[misc]  # pylint: disable=line-too-long
  """HTTP request logs."""

  # khaleesi.ninja.
  language = models.TextField(default = 'UNKNOWN')
  deviceId = models.TextField(default = 'UNKNOWN')

  # HTTP.
  languageHeader = models.TextField(default = 'UNKNOWN')
  ip             = models.TextField(default = 'UNKNOWN')
  useragent      = models.TextField(default = 'UNKNOWN')

  # Processed.
  geolocation    = models.TextField(default = 'UNKNOWN')
  browser        = models.TextField(default = 'UNKNOWN')
  renderingAgent = models.TextField(default = 'UNKNOWN')
  os             = models.TextField(default = 'UNKNOWN')
  deviceType     = models.TextField(default = 'UNKNOWN')

  objects: models.Manager[HttpRequest]


  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcHttpRequest,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    errors: List[str] = []

    if self._state.adding:
      # khaleesi.ninja.
      self.language = grpc.request.language
      self.deviceId = grpc.request.deviceId

      # HTTP.
      self.languageHeader = grpc.request.languageHeader
      self.ip             = grpc.request.ip
      self.useragent      = grpc.request.useragent

      # Processed.
      # TODO(49): Digest useragent.
      self.geolocation    = ''
      self.browser        = ''
      self.renderingAgent = ''
      self.os             = ''
      self.deviceType     = ''

    # Needs to be at the end because it saves errors to the model.
    self.responseMetadataFromGrpc(
      metadata = grpc.responseMetadata,
      grpc     = grpc.response,
      errors   = errors,
    )
    self.metadataFromGrpc(grpc = grpc.requestMetadata, errors = errors)
    super().khaleesiSave(*args, metadata = metadata, grpc = grpc, **kwargs)

  def toGrpc(self) -> GrpcHttpRequest :
    """Return a grpc object containing own values."""
    grpc = GrpcHttpRequest()
    self.metadataToGrpc(logMetadata = grpc.logMetadata, requestMetadata = grpc.requestMetadata)
    self.responseMetadataToGrpc(
      logMetadata = grpc.responseLogMetadata,
      processed   = grpc.processedResponse,
      response    = grpc.response,
    )

    # khaleesi.ninja.
    grpc.request.language = self.language
    grpc.request.deviceId = self.deviceId

    # HTTP.
    grpc.request.languageHeader = self.languageHeader
    grpc.request.ip             = self.ip
    grpc.request.useragent      = self.useragent

    # Processed.
    grpc.request.geolocation    = self.geolocation
    grpc.request.browser        = self.browser
    grpc.request.renderingAgent = self.renderingAgent
    grpc.request.os             = self.os
    grpc.request.deviceType     = self.deviceType

    return grpc

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    metadata = super().toObjectMetadata()
    metadata.id = self.metaCallerHttpRequestId
    return metadata
