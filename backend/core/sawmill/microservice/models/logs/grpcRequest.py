"""Request logs."""

# pylint:disable=duplicate-code

# Python.
from __future__ import annotations
from typing import List, Any

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Model, Manager
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_pb2 import ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import GrpcRequestRequest as GrpcGrpcRequest
from microservice.models.logs.metadataMixin import GrpcMetadataMixin
from microservice.models.logs.responseMetadataMixin import ResponseMetadataMixin


class GrpcRequest(Model[GrpcGrpcRequest], GrpcMetadataMixin, ResponseMetadataMixin):  # type: ignore[misc]  # pylint: disable=line-too-long
  """Request logs."""

  upstreamRequestId      = models.TextField(default = 'UNKNOWN')
  upstreamRequestSite    = models.TextField(default = 'UNKNOWN')
  upstreamRequestApp     = models.TextField(default = 'UNKNOWN')
  upstreamRequestService = models.TextField(default = 'UNKNOWN')
  upstreamRequestMethod  = models.TextField(default = 'UNKNOWN')
  upstreamRequestPodId   = models.TextField(default = 'UNKNOWN')

  objects: Manager[GrpcRequest]  # type: ignore[assignment]


  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcGrpcRequest,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    errors: List[str] = []

    if self._state.adding:
      self.upstreamRequestId = parseString(
        raw    = grpc.request.upstreamRequest.requestId,
        name   = 'upstreamRequestRequestId',
        errors = errors,
      )
      self.upstreamRequestSite = parseString(
        raw    = grpc.request.upstreamRequest.site,
        name   = 'upstreamRequestSite',
        errors = errors,
      )
      self.upstreamRequestApp = parseString(
        raw    = grpc.request.upstreamRequest.app,
        name   = 'upstreamRequestApp',
        errors = errors,
      )
      self.upstreamRequestService = parseString(
        raw    = grpc.request.upstreamRequest.service,
        name   = 'upstreamRequestService',
        errors = errors,
      )
      self.upstreamRequestMethod = parseString(
        raw    = grpc.request.upstreamRequest.method,
        name   = 'upstreamRequestMethod',
        errors = errors,
      )
      self.upstreamRequestPodId = parseString(
        raw    = grpc.request.upstreamRequest.podId,
        name   = 'upstreamRequestPodId',
        errors = errors,
      )

    # Needs to be at the end because it saves errors to the model.
    self.responseMetadataFromGrpc(
      metadata = grpc.responseMetadata,
      grpc     = grpc.response,
      errors   = errors,
    )
    self.metadataFromGrpc(grpc = grpc.requestMetadata, errors = errors)
    super().khaleesiSave(*args, metadata = metadata, grpc = grpc, **kwargs)

  def toGrpc(self) -> GrpcGrpcRequest :
    """Return a grpc object containing own values."""
    grpc = GrpcGrpcRequest()
    self.metadataToGrpc(logMetadata = grpc.logMetadata, requestMetadata = grpc.requestMetadata)
    self.responseMetadataToGrpc(
      logMetadata = grpc.responseLogMetadata,
      processed   = grpc.processedResponse,
      response    = grpc.response,
    )

    # Upstream request.
    grpc.request.upstreamRequest.requestId = self.upstreamRequestId
    grpc.request.upstreamRequest.site      = self.upstreamRequestSite
    grpc.request.upstreamRequest.app       = self.upstreamRequestApp
    grpc.request.upstreamRequest.service   = self.upstreamRequestService
    grpc.request.upstreamRequest.method    = self.upstreamRequestMethod
    grpc.request.upstreamRequest.podId     = self.upstreamRequestPodId

    return grpc

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    metadata = super().toObjectMetadata()
    metadata.id = self.metaCallerGrpcRequestId
    return metadata
