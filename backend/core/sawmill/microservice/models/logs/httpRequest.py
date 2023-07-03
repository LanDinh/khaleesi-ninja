"""Request logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_pb2 import EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequest as GrpcHttpRequest,
  HttpRequestResponse as GrpcHttpRequestResponse,
  HttpResponseRequest as GrpcHttpResponseRequest,
)
from microservice.models.logs.abstractResponse import ResponseMetadata
from microservice.models.logs.grpcRequest import GrpcRequest


class HttpRequestManager(models.Manager['HttpRequest']):
  """Custom model manager."""

  def logRequest(self, *, grpcRequest: GrpcHttpRequest) -> HttpRequest :
    """Log a gRPC HTTP request."""

    errors: List[str] = []

    return self.create(
      # khaleesi.ninja.
      type     = GrpcHttpRequestResponse.RequestType.Name(GrpcHttpRequestResponse.RequestType.USER),
      language = parseString(raw = grpcRequest.language, name = 'language', errors = errors),
      deviceId = parseString(raw = grpcRequest.deviceId, name = 'deviceId', errors = errors),
      # Http.
      languageHeader = parseString(
        raw    = grpcRequest.languageHeader,
        name   = 'languageHeader',
        errors = errors,
      ),
      ip = parseString(raw = grpcRequest.ip, name = 'ip', errors = errors),
      useragent = parseString(
        raw    = grpcRequest.useragent,
        name   = 'useragent',
        errors = errors,
      ),
      # Processed.
      # Metadata.
      **self.model.logMetadata(metadata = grpcRequest.requestMetadata, errors = errors),
    )

  def logSystemRequest(self, *, grpcRequest: EmptyRequest) -> HttpRequest :
    """Log a gRPC HTTP request."""

    errors: List[str] = []

    return self.create(
      # khaleesi.ninja.
      type = GrpcHttpRequestResponse.RequestType.Name(GrpcHttpRequestResponse.RequestType.SYSTEM),
      # Metadata.
      **self.model.logMetadata(metadata = grpcRequest.requestMetadata, errors = errors),
    )

  def logResponse(self, *, grpcResponse: GrpcHttpResponseRequest) -> HttpRequest :
    """Log a gRPC HTTP response."""
    request = self.get(
      metaCallerHttpRequestId = grpcResponse.requestMetadata.httpCaller.requestId,
      metaResponseStatus      = 'IN_PROGRESS',
    )
    request.logResponse(grpcResponse = grpcResponse.response)
    request.save()
    return request

  def addChildDuration(self, *, request: GrpcRequest) -> None :
    """Log request duration."""
    httpRequest = self.get(
      metaCallerHttpRequestId = request.metaCallerHttpRequestId,
      metaResponseStatus      = 'IN_PROGRESS',
    )
    httpRequest.metaChildDuration += request.reportedDuration
    httpRequest.save()


class HttpRequest(ResponseMetadata):
  """HTTP request logs."""

  # khaleesi.ninja.
  type     = models.TextField(default = 'UNKNOWN')
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

  objects = HttpRequestManager()

  def toGrpc(self) -> GrpcHttpRequestResponse :
    """Map to gRPC HTTP request message."""

    grpc = GrpcHttpRequestResponse()

    # Request metadata.
    self.requestMetadataToGrpc(requestMetadata = grpc.request.requestMetadata)
    self.responseMetadataToGrpc(responseMetadata = grpc.requestMetadata)

    # Response.
    self.responseToGrpc(
      metadata  = grpc.responseMetadata,
      response  = grpc.response,
      processed = grpc.processedResponse,
    )

    # khaleesi.ninja.
    grpc.request.language = self.language
    grpc.request.deviceId = self.deviceId

    # HTTP.
    grpc.request.languageHeader = self.languageHeader
    grpc.request.ip             = self.ip
    grpc.request.useragent      = self.useragent

    # Processed.
    grpc.type = GrpcHttpRequestResponse.RequestType.Value(self.type)
    grpc.geolocation    = self.geolocation
    grpc.browser        = self.browser
    grpc.renderingAgent = self.renderingAgent
    grpc.os             = self.os
    grpc.deviceType     = self.deviceType

    return grpc
