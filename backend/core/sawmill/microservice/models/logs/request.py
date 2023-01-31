"""Request logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parse_util import parse_string
from khaleesi.proto.core_sawmill_pb2 import (
  Request as GrpcRequest, RequestResponse as GrpcRequestResponse,
  ResponseRequest as GrpcResponse,
)
from microservice.models.logs.abstract_response import ResponseMetadata


class RequestManager(models.Manager['Request']):
  """Custom model manager."""

  def log_request(self, *, grpc_request: GrpcRequest) -> Request :
    """Log a gRPC request."""

    errors: List[str] = []

    upstream_request = {} if grpc_request is None else {
        "upstream_request_request_id": parse_string(
          raw = grpc_request.upstream_request.request_id,
          name = 'upstream_request_request_id',
          errors = errors,
        ),
        "upstream_request_khaleesi_gate": parse_string(
          raw = grpc_request.upstream_request.khaleesi_gate,
          name = 'upstream_request_khaleesi_gate',
          errors = errors,
        ),
        "upstream_request_khaleesi_service": parse_string(
          raw = grpc_request.upstream_request.khaleesi_service,
          name = 'upstream_request_khaleesi_service',
          errors = errors,
        ),
        "upstream_request_grpc_service": parse_string(
          raw = grpc_request.upstream_request.grpc_service,
          name = 'upstream_request_grpc_service',
          errors = errors,
        ),
        "upstream_request_grpc_method": parse_string(
          raw = grpc_request.upstream_request.grpc_method,
          name = 'upstream_request_grpc_method',
          errors = errors,
        ),
    }

    return self.create(
      # Upstream request.
      **upstream_request,
      # Metadata.
      **self.model.log_metadata(metadata = grpc_request.request_metadata, errors = errors),
    )

  def log_response(self, *, grpc_response: GrpcResponse) -> Request :
    """Log a gRPC response."""
    request = self.get(
      meta_caller_request_id = grpc_response.request_metadata.caller.request_id,
      meta_response_status   = 'IN_PROGRESS',
    )
    request.log_response(grpc_response = grpc_response.response)
    request.save()
    return request


class Request(ResponseMetadata):
  """Request logs."""

  upstream_request_request_id       = models.TextField(default = 'UNKNOWN')
  upstream_request_khaleesi_gate    = models.TextField(default = 'UNKNOWN')
  upstream_request_khaleesi_service = models.TextField(default = 'UNKNOWN')
  upstream_request_grpc_service     = models.TextField(default = 'UNKNOWN')
  upstream_request_grpc_method      = models.TextField(default = 'UNKNOWN')

  objects = RequestManager()

  def to_grpc_request_response(self) -> GrpcRequestResponse :
    """Map to gRPC event message."""

    grpc_request_response = GrpcRequestResponse()

    # Request metadata.
    self.request_metadata_to_grpc(request_metadata = grpc_request_response.request.request_metadata)
    self.response_metadata_to_grpc(response_metadata = grpc_request_response.request_metadata)

    # Response.
    self.response_to_grpc(
      metadata = grpc_request_response.response_metadata,
      response = grpc_request_response.response,
      processed = grpc_request_response.processed_response,
    )

    # Upstream request.
    grpc_request_response.request.upstream_request.request_id = self.upstream_request_request_id
    grpc_request_response.request.upstream_request.khaleesi_gate = \
      self.upstream_request_khaleesi_gate
    grpc_request_response.request.upstream_request.khaleesi_service = \
      self.upstream_request_khaleesi_service
    grpc_request_response.request.upstream_request.grpc_service = \
      self.upstream_request_grpc_service
    grpc_request_response.request.upstream_request.grpc_method = self.upstream_request_grpc_method

    return grpc_request_response
