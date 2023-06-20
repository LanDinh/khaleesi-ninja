"""Request logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parse_util import parse_string
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest as GrpcGrpcRequest, GrpcRequestResponse as GrpcGrpcRequestResponse,
  GrpcResponseRequest as GrpcGrpcResponse,
)
from microservice.models.logs.abstract_response import ResponseMetadata


class GrpcRequestManager(models.Manager['GrpcRequest']):
  """Custom model manager."""

  def log_request(self, *, grpc_request: GrpcGrpcRequest) -> GrpcRequest :
    """Log a gRPC request."""

    errors: List[str] = []

    upstream_request = {} if grpc_request is None else {
        "upstream_request_grpc_request_id": parse_string(
          raw = grpc_request.upstreamRequest.grpcRequestId,
          name = 'upstream_request_grpc_request_id',
          errors = errors,
        ),
        "upstream_request_khaleesi_gate": parse_string(
          raw = grpc_request.upstreamRequest.khaleesiGate,
          name = 'upstream_request_khaleesi_gate',
          errors = errors,
        ),
        "upstream_request_khaleesi_service": parse_string(
          raw = grpc_request.upstreamRequest.khaleesiService,
          name = 'upstream_request_khaleesi_service',
          errors = errors,
        ),
        "upstream_request_grpc_service": parse_string(
          raw = grpc_request.upstreamRequest.grpcService,
          name = 'upstream_request_grpc_service',
          errors = errors,
        ),
        "upstream_request_grpc_method": parse_string(
          raw = grpc_request.upstreamRequest.grpcMethod,
          name = 'upstream_request_grpc_method',
          errors = errors,
        ),
    }

    return self.create(
      # Upstream request.
      **upstream_request,
      # Metadata.
      **self.model.log_metadata(metadata = grpc_request.requestMetadata, errors = errors),
    )

  def log_response(self, *, grpc_response: GrpcGrpcResponse) -> GrpcRequest :
    """Log a gRPC response."""
    request = self.get(
      meta_caller_grpc_request_id = grpc_response.requestMetadata.caller.grpcRequestId,
      meta_response_status        = 'IN_PROGRESS',
    )
    request.log_response(grpc_response = grpc_response.response)
    request.save()
    return request


class GrpcRequest(ResponseMetadata):
  """Request logs."""

  upstream_request_grpc_request_id  = models.TextField(default = 'UNKNOWN')
  upstream_request_khaleesi_gate    = models.TextField(default = 'UNKNOWN')
  upstream_request_khaleesi_service = models.TextField(default = 'UNKNOWN')
  upstream_request_grpc_service     = models.TextField(default = 'UNKNOWN')
  upstream_request_grpc_method      = models.TextField(default = 'UNKNOWN')

  objects = GrpcRequestManager()

  def to_grpc_request_response(self) -> GrpcGrpcRequestResponse :
    """Map to gRPC event message."""

    grpc_request_response = GrpcGrpcRequestResponse()

    # Request metadata.
    self.request_metadata_to_grpc(request_metadata = grpc_request_response.request.requestMetadata)
    self.response_metadata_to_grpc(response_metadata = grpc_request_response.requestMetadata)

    # Response.
    self.response_to_grpc(
      metadata = grpc_request_response.responseMetadata,
      response = grpc_request_response.response,
      processed = grpc_request_response.processedResponse,
    )

    # Upstream request.
    grpc_request_response.request.upstreamRequest.grpcRequestId = \
      self.upstream_request_grpc_request_id
    grpc_request_response.request.upstreamRequest.khaleesiGate = self.upstream_request_khaleesi_gate
    grpc_request_response.request.upstreamRequest.khaleesiService = \
      self.upstream_request_khaleesi_service
    grpc_request_response.request.upstreamRequest.grpcService = self.upstream_request_grpc_service
    grpc_request_response.request.upstreamRequest.grpcMethod = self.upstream_request_grpc_method

    return grpc_request_response
