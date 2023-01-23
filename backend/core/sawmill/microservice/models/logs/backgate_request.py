"""Request logs."""

# Python.
from __future__ import annotations
from typing import List, Tuple

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.job import job
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobCleanupRequest
from khaleesi.proto.core_sawmill_pb2 import (
  BackgateRequest as GrpcBackgateRequest,
  BackgateRequestResponse as GrpcBackgateRequestResponse,
  EmptyRequest,
  BackgateResponseRequest as GrpcBackgateResponseRequest,
)
from microservice.models.logs.abstract_response import ResponseMetadata
from microservice.models.logs.request import Request
from microservice.parse_util import parse_string


class BackgateRequestManager(models.Manager['BackgateRequest']):
  """Custom model manager."""

  @job()
  def cleanup(
      self,
      request: JobCleanupRequest,
  ) -> Tuple['JobExecutionResponse.Status.V', int, str] :
    """Cleanup"""
    return JobExecutionResponse.Status.SUCCESS, 0, 'Job done.'

  def log_backgate_request(self, *, grpc_backgate_request: GrpcBackgateRequest) -> BackgateRequest :
    """Log a gRPC backgate request."""

    errors: List[str] = []

    language_header = parse_string(
      raw    = grpc_backgate_request.language_header,
      name   = 'language_header',
      errors = errors,
    )
    useragent = parse_string(
      raw    = grpc_backgate_request.useragent,
      name   = 'useragent',
      errors = errors,
    )
    ip = parse_string(raw = grpc_backgate_request.ip, name = 'ip', errors = errors)  # pylint: disable=invalid-name

    return self.create(
      # khaleesi.ninja.
      type = GrpcBackgateRequestResponse.RequestType.Name(
        GrpcBackgateRequestResponse.RequestType.USER,
      ),
      language = parse_string(
        raw = grpc_backgate_request.language,
        name = 'language',
        errors = errors,
      ),
      device_id = parse_string(
        raw = grpc_backgate_request.device_id,
        name = 'device_id',
        errors = errors,
      ),
      # Http.
      language_header = language_header,
      ip = ip,
      useragent = useragent,
      # Processed.
      # Metadata.
      **self.model.log_metadata(metadata = grpc_backgate_request.request_metadata, errors = errors),
    )

  def log_system_backgate_request(self, *, grpc_backgate_request: EmptyRequest) -> BackgateRequest :
    """Log a gRPC backgate request."""

    errors: List[str] = []

    return self.create(
      # khaleesi.ninja.
      type = GrpcBackgateRequestResponse.RequestType.Name(
        GrpcBackgateRequestResponse.RequestType.SYSTEM,
      ),
      # Metadata.
      **self.model.log_metadata(metadata = grpc_backgate_request.request_metadata, errors = errors),
    )

  def log_response(self, *, grpc_response: GrpcBackgateResponseRequest) -> BackgateRequest :
    """Log a gRPC backgate response."""
    request = self.get(
      meta_caller_backgate_request_id = grpc_response.request_metadata.caller.backgate_request_id,
      meta_response_status            = 'IN_PROGRESS',
    )
    request.log_response(grpc_response = grpc_response.response)
    request.save()
    return request

  def add_child_duration(self, *, request: Request) -> None :
    """Log request duration."""
    backgate_request = self.get(
      meta_caller_backgate_request_id = request.meta_caller_backgate_request_id,
      meta_response_status            = 'IN_PROGRESS',
    )
    backgate_request.meta_child_duration += request.reported_duration
    backgate_request.save()


class BackgateRequest(ResponseMetadata):
  """Backgate request logs."""

  # khaleesi.ninja.
  type      = models.TextField(default = 'UNKNOWN')
  language  = models.TextField(default = 'UNKNOWN')
  device_id = models.TextField(default = 'UNKNOWN')

  # HTTP.
  language_header = models.TextField(default = 'UNKNOWN')
  ip              = models.TextField(default = 'UNKNOWN')
  useragent       = models.TextField(default = 'UNKNOWN')

  # Processed.
  geolocation     = models.TextField(default = 'UNKNOWN')
  browser         = models.TextField(default = 'UNKNOWN')
  rendering_agent = models.TextField(default = 'UNKNOWN')
  os              = models.TextField(default = 'UNKNOWN')
  device_type     = models.TextField(default = 'UNKNOWN')

  objects = BackgateRequestManager()

  def to_grpc_backgate_request_response(self) -> GrpcBackgateRequestResponse :
    """Map to gRPC backgate request message."""

    grpc_backgate_request_response = GrpcBackgateRequestResponse()

    # Request metadata.
    self.request_metadata_to_grpc(
      request_metadata = grpc_backgate_request_response.request.request_metadata,
    )
    self.response_metadata_to_grpc(
      response_metadata = grpc_backgate_request_response.request_metadata,
    )

    # Response.
    self.response_to_grpc(
      metadata = grpc_backgate_request_response.response_metadata,
      response = grpc_backgate_request_response.response,
      processed = grpc_backgate_request_response.processed_response,
    )

    # khaleesi.ninja.
    grpc_backgate_request_response.request.language  = self.language
    grpc_backgate_request_response.request.device_id = self.device_id

    # HTTP.
    grpc_backgate_request_response.request.language_header = self.language_header
    grpc_backgate_request_response.request.ip              = self.ip
    grpc_backgate_request_response.request.useragent       = self.useragent

    # Processed.
    grpc_backgate_request_response.type = GrpcBackgateRequestResponse.RequestType.Value(self.type)
    grpc_backgate_request_response.geolocation     = self.geolocation
    grpc_backgate_request_response.browser         = self.browser
    grpc_backgate_request_response.rendering_agent = self.rendering_agent
    grpc_backgate_request_response.os              = self.os
    grpc_backgate_request_response.device_type     = self.device_type

    return grpc_backgate_request_response
