"""Request logs."""

# Python.
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_sawmill_pb2 import (
    Request as GrpcRequest, RequestResponse as GrpcRequestResponse,
    ResponseRequest as GrpcResponse,
)
from microservice.models.abstract import Metadata
from microservice.parse_util import parse_timestamp, parse_string


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

    errors: List[str] = []

    request = self.get(
      meta_caller_request_id = grpc_response.request_id,
      response_status = 'IN_PROGRESS',
    )
    if grpc_response.response.status:
      request.response_status = grpc_response.response.status
    else:
      errors.append('response status is missing')
      request.response_status = 'UNKNOWN'
    response_timestamp =  parse_timestamp(
      raw    = grpc_response.response.timestamp.ToDatetime(),
      name   = 'timestamp',
      errors = errors,
    )
    if response_timestamp:
      request.response_reported_timestamp = response_timestamp
    request.response_logging_errors = '\n'.join(errors)
    request.save()

    return request


class Request(Metadata):
  """Request logs."""

  upstream_request_request_id       = models.TextField(default = 'UNKNOWN')
  upstream_request_khaleesi_gate    = models.TextField(default = 'UNKNOWN')
  upstream_request_khaleesi_service = models.TextField(default = 'UNKNOWN')
  upstream_request_grpc_service     = models.TextField(default = 'UNKNOWN')
  upstream_request_grpc_method      = models.TextField(default = 'UNKNOWN')

  response_status             = models.TextField(default = 'IN_PROGRESS')
  response_reported_timestamp = models.DateTimeField(
    default = datetime.min.replace(tzinfo = timezone.utc))
  response_logged_timestamp   = models.DateTimeField(auto_now = True)
  response_logging_errors     = models.TextField(blank = True)

  objects = RequestManager()

  @property
  def is_in_progress(self) -> bool :
    """Check if the request is still in progress."""
    return self.response_status == 'IN_PROGRESS'

  @property
  def reported_duration(self) -> timedelta :
    """Get the reported duration."""
    if self.is_in_progress or \
        self.meta_reported_timestamp == datetime.min.replace(tzinfo = timezone.utc) or \
        self.response_reported_timestamp == datetime.min.replace(tzinfo = timezone.utc):
      return timedelta()
    return self.response_reported_timestamp - self.meta_reported_timestamp

  @property
  def logged_duration(self) -> timedelta :
    """Get the logged duration."""
    if self.is_in_progress:
      return timedelta()
    return self.response_logged_timestamp - self.meta_logged_timestamp

  def to_grpc_request_response(self) -> GrpcRequestResponse :
    """Map to gRPC event message."""

    grpc_request_response = GrpcRequestResponse()
    # Request metadata.
    self.request_metadata_to_grpc(request_metadata = grpc_request_response.request.request_metadata)
    self.response_metadata_to_grpc(response_metadata = grpc_request_response.request_metadata)
    grpc_request_response.request.request_metadata.caller.request_id = self.meta_caller_request_id
    # Upstream request.
    grpc_request_response.request.upstream_request.request_id = self.upstream_request_request_id
    grpc_request_response.request.upstream_request.khaleesi_gate = \
      self.upstream_request_khaleesi_gate
    grpc_request_response.request.upstream_request.khaleesi_service = \
      self.upstream_request_khaleesi_service
    grpc_request_response.request.upstream_request.grpc_service = \
      self.upstream_request_grpc_service
    grpc_request_response.request.upstream_request.grpc_method = self.upstream_request_grpc_method
    # Response.
    grpc_request_response.response_metadata.logged_timestamp.FromDatetime(
      self.response_logged_timestamp,
    )
    grpc_request_response.response_metadata.errors = self.response_logging_errors
    grpc_request_response.response.timestamp.FromDatetime(self.response_reported_timestamp)
    grpc_request_response.response.status = self.response_status
    # Durations.
    grpc_request_response.logged_duration.FromTimedelta(self.logged_duration)
    grpc_request_response.reported_duration.FromTimedelta(self.reported_duration)

    return grpc_request_response
