"""Request logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_sawmill_pb2 import (
    Request as GrpcRequest,
    RequestResponse as GrpcRequestResponse,
)
from microservice.models.abstract import Metadata
from microservice.parse_util import parse_string


class RequestManager(models.Manager['Request']):
  """Custom model manager."""

  def log_request(self, *, grpc_request: GrpcRequest) -> Request :
    """Log a gRPC event."""

    errors: List[str] = []

    return self.create(
      # Upstream request.
      upstream_request_request_id = grpc_request.upstream_request.request_id,
      upstream_request_khaleesi_gate = parse_string(
        raw = grpc_request.upstream_request.khaleesi_gate,
        name = 'upstream_request_khaleesi_gate',
        errors = errors,
      ),
      upstream_request_khaleesi_service = parse_string(
        raw = grpc_request.upstream_request.khaleesi_service,
        name = 'upstream_request_khaleesi_service',
        errors = errors,
      ),
      upstream_request_grpc_service = parse_string(
        raw = grpc_request.upstream_request.grpc_service,
        name = 'upstream_request_grpc_service',
        errors = errors,
      ),
      upstream_request_grpc_method = parse_string(
        raw = grpc_request.upstream_request.grpc_method,
        name = 'upstream_request_grpc_method',
        errors = errors,
      ),
      # Metadata.
      **self.model.log_metadata(metadata = grpc_request.request_metadata, errors = errors),
    )


class Request(Metadata):
  """Request logs."""

  upstream_request_request_id       = models.BigIntegerField(default = 0)
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
    self.response_metadata_to_grpc(response_metadata = grpc_request_response.response_metadata)
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
