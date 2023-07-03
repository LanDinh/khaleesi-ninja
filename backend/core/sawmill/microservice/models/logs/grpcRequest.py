"""Request logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest as GrpcGrpcRequest, GrpcRequestResponse as GrpcGrpcRequestResponse,
  GrpcResponseRequest as GrpcGrpcResponse,
)
from microservice.models.logs.abstractResponse import ResponseMetadata


class GrpcRequestManager(models.Manager['GrpcRequest']):
  """Custom model manager."""

  def logRequest(self, *, grpcRequest: GrpcGrpcRequest) -> GrpcRequest :
    """Log a gRPC request."""

    errors: List[str] = []

    upstreamRequest = {} if grpcRequest is None else {
        "upstreamRequestGrpcRequestId": parseString(
          raw    = grpcRequest.upstreamRequest.requestId,
          name   = 'upstreamRequestGrpcRequestId',
          errors = errors,
        ),
        "upstreamRequestKhaleesiGate": parseString(
          raw    = grpcRequest.upstreamRequest.khaleesiGate,
          name   = 'upstreamRequestKhaleesiGate',
          errors = errors,
        ),
        "upstreamRequestKhaleesiService": parseString(
          raw    = grpcRequest.upstreamRequest.khaleesiService,
          name   = 'upstreamRequestKhaleesiService',
          errors = errors,
        ),
        "upstreamRequestGrpcService": parseString(
          raw    = grpcRequest.upstreamRequest.grpcService,
          name   = 'upstreamRequestGrpcService',
          errors = errors,
        ),
        "upstreamRequestGrpcMethod": parseString(
          raw    = grpcRequest.upstreamRequest.grpcMethod,
          name   = 'upstreamRequestGrpcMethod',
          errors = errors,
        ),
    }

    return self.create(
      # Upstream request.
      **upstreamRequest,
      # Metadata.
      **self.model.logMetadata(metadata = grpcRequest.requestMetadata, errors = errors),
    )

  def logResponse(self, *, grpcResponse: GrpcGrpcResponse) -> GrpcRequest :
    """Log a gRPC response."""
    request = self.get(
      metaCallerGrpcRequestId = grpcResponse.requestMetadata.grpcCaller.requestId,
      metaResponseStatus      = 'IN_PROGRESS',
    )
    request.logResponse(grpcResponse = grpcResponse.response)
    request.save()
    return request


class GrpcRequest(ResponseMetadata):
  """Request logs."""

  upstreamRequestGrpcRequestId   = models.TextField(default = 'UNKNOWN')
  upstreamRequestKhaleesiGate    = models.TextField(default = 'UNKNOWN')
  upstreamRequestKhaleesiService = models.TextField(default = 'UNKNOWN')
  upstreamRequestGrpcService     = models.TextField(default = 'UNKNOWN')
  upstreamRequestGrpcMethod      = models.TextField(default = 'UNKNOWN')

  objects = GrpcRequestManager()

  def toGrpc(self) -> GrpcGrpcRequestResponse :
    """Map to gRPC event message."""

    grpcRequestResponse = GrpcGrpcRequestResponse()

    # Request metadata.
    self.requestMetadataToGrpc(requestMetadata = grpcRequestResponse.request.requestMetadata)
    self.responseMetadataToGrpc(responseMetadata = grpcRequestResponse.requestMetadata)

    # Response.
    self.responseToGrpc(
      metadata  = grpcRequestResponse.responseMetadata,
      response  = grpcRequestResponse.response,
      processed = grpcRequestResponse.processedResponse,
    )

    # Upstream request.
    grpcRequestResponse.request.upstreamRequest.requestId = self.upstreamRequestGrpcRequestId
    grpcRequestResponse.request.upstreamRequest.khaleesiGate = self.upstreamRequestKhaleesiGate
    grpcRequestResponse.request.upstreamRequest.khaleesiService = \
      self.upstreamRequestKhaleesiService
    grpcRequestResponse.request.upstreamRequest.grpcService = self.upstreamRequestGrpcService
    grpcRequestResponse.request.upstreamRequest.grpcMethod = self.upstreamRequestGrpcMethod

    return grpcRequestResponse
