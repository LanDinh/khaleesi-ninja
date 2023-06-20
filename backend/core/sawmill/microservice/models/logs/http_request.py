"""Request logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parse_util import parse_string
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequest as GrpcHttpRequest,
  HttpRequestResponse as GrpcHttpRequestResponse,
  EmptyRequest,
  HttpResponseRequest as GrpcHttpResponseRequest,
)
from microservice.models.logs.abstract_response import ResponseMetadata
from microservice.models.logs.grpc_request import GrpcRequest


class HttpRequestManager(models.Manager['HttpRequest']):
  """Custom model manager."""

  def log_request(self, *, grpc_request: GrpcHttpRequest) -> HttpRequest :
    """Log a gRPC HTTP request."""

    errors: List[str] = []

    language_header = parse_string(
      raw    = grpc_request.languageHeader,
      name   = 'language_header',
      errors = errors,
    )
    useragent = parse_string(
      raw    = grpc_request.useragent,
      name   = 'useragent',
      errors = errors,
    )
    ip = parse_string(raw = grpc_request.ip, name = 'ip', errors = errors)  # pylint: disable=invalid-name

    return self.create(
      # khaleesi.ninja.
      type = GrpcHttpRequestResponse.RequestType.Name(GrpcHttpRequestResponse.RequestType.USER),
      language = parse_string(
        raw = grpc_request.language,
        name = 'language',
        errors = errors,
      ),
      device_id = parse_string(
        raw = grpc_request.deviceId,
        name = 'device_id',
        errors = errors,
      ),
      # Http.
      language_header = language_header,
      ip = ip,
      useragent = useragent,
      # Processed.
      # Metadata.
      **self.model.log_metadata(metadata = grpc_request.requestMetadata, errors = errors),
    )

  def log_system_request(self, *, grpc_request: EmptyRequest) -> HttpRequest :
    """Log a gRPC HTTP request."""

    errors: List[str] = []

    return self.create(
      # khaleesi.ninja.
      type = GrpcHttpRequestResponse.RequestType.Name(GrpcHttpRequestResponse.RequestType.SYSTEM),
      # Metadata.
      **self.model.log_metadata(metadata = grpc_request.requestMetadata, errors = errors),
    )

  def log_response(self, *, grpc_response: GrpcHttpResponseRequest) -> HttpRequest :
    """Log a gRPC HTTP response."""
    request = self.get(
      meta_caller_http_request_id = grpc_response.requestMetadata.caller.httpRequestId,
      meta_response_status            = 'IN_PROGRESS',
    )
    request.log_response(grpc_response = grpc_response.response)
    request.save()
    return request

  def add_child_duration(self, *, request: GrpcRequest) -> None :
    """Log request duration."""
    http_request = self.get(
      meta_caller_http_request_id = request.meta_caller_http_request_id,
      meta_response_status        = 'IN_PROGRESS',
    )
    http_request.meta_child_duration += request.reported_duration
    http_request.save()


class HttpRequest(ResponseMetadata):
  """HTTP request logs."""

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

  objects = HttpRequestManager()

  def to_grpc_backgate_request_response(self) -> GrpcHttpRequestResponse :
    """Map to gRPC HTTP request message."""

    grpc = GrpcHttpRequestResponse()

    # Request metadata.
    self.request_metadata_to_grpc(request_metadata = grpc.request.requestMetadata)
    self.response_metadata_to_grpc(response_metadata = grpc.requestMetadata)

    # Response.
    self.response_to_grpc(
      metadata  = grpc.responseMetadata,
      response  = grpc.response,
      processed = grpc.processedResponse,
    )

    # khaleesi.ninja.
    grpc.request.language = self.language
    grpc.request.deviceId = self.device_id

    # HTTP.
    grpc.request.languageHeader = self.language_header
    grpc.request.ip             = self.ip
    grpc.request.useragent      = self.useragent

    # Processed.
    grpc.type = GrpcHttpRequestResponse.RequestType.Value(self.type)
    grpc.geolocation    = self.geolocation
    grpc.browser        = self.browser
    grpc.renderingAgent = self.rendering_agent
    grpc.os             = self.os
    grpc.deviceType     = self.device_type

    return grpc
