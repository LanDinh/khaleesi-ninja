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

  upstreamRequestId              = models.TextField(default = 'UNKNOWN')
  upstreamRequestKhaleesiGate    = models.TextField(default = 'UNKNOWN')
  upstreamRequestKhaleesiService = models.TextField(default = 'UNKNOWN')
  upstreamRequestGrpcService     = models.TextField(default = 'UNKNOWN')
  upstreamRequestGrpcMethod      = models.TextField(default = 'UNKNOWN')
  upstreamRequestPodId           = models.TextField(default = 'UNKNOWN')

  objects: Manager[GrpcRequest]


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
        name   = 'upstreamRequestGrpcRequestId',
        errors = errors,
      )
      self.upstreamRequestKhaleesiGate = parseString(
        raw    = grpc.request.upstreamRequest.khaleesiGate,
        name   = 'upstreamRequestKhaleesiGate',
        errors = errors,
      )
      self.upstreamRequestKhaleesiService = parseString(
        raw    = grpc.request.upstreamRequest.khaleesiService,
        name   = 'upstreamRequestKhaleesiService',
        errors = errors,
      )
      self.upstreamRequestGrpcService = parseString(
        raw    = grpc.request.upstreamRequest.grpcService,
        name   = 'upstreamRequestGrpcService',
        errors = errors,
      )
      self.upstreamRequestGrpcMethod = parseString(
        raw    = grpc.request.upstreamRequest.grpcMethod,
        name   = 'upstreamRequestGrpcMethod',
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
    grpc.request.upstreamRequest.requestId       = self.upstreamRequestId
    grpc.request.upstreamRequest.khaleesiGate    = self.upstreamRequestKhaleesiGate
    grpc.request.upstreamRequest.khaleesiService = self.upstreamRequestKhaleesiService
    grpc.request.upstreamRequest.grpcService     = self.upstreamRequestGrpcService
    grpc.request.upstreamRequest.grpcMethod      = self.upstreamRequestGrpcMethod
    grpc.request.upstreamRequest.podId           = self.upstreamRequestPodId

    return grpc

  def toObjectMetadata(self) -> ObjectMetadata :
    """Return the object metadata representing this object."""
    metadata = super().toObjectMetadata()
    metadata.id = self.metaCallerGrpcRequestId
    return metadata
