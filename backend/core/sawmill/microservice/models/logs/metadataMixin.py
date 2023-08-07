"""core-sawmill abstract logs models."""

from __future__ import annotations

# Python.
from datetime import datetime, timezone
from typing import Callable, List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parseUtil import parseTimestamp, parseString
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import LogRequestMetadata


MIN_TIMESTAMP = datetime.min.replace(tzinfo = timezone.utc)


class MetadataMixin(models.Model):
  """Common metadata."""

  # HTTP caller.
  metaCallerHttpRequestId = models.TextField(default = 'UNKNOWN')
  metaCallerHttpSite      = models.TextField(default = 'UNKNOWN')
  metaCallerHttpPath      = models.TextField(default = 'UNKNOWN')
  metaCallerHttpPodId     = models.TextField(default = 'UNKNOWN')

  # User.
  metaUserId   = models.TextField(default = 'UNKNOWN')
  metaUserType = models.TextField(default = 'UNKNOWN')

  # Misc.
  metaReportedTimestamp = models.DateTimeField(default = MIN_TIMESTAMP)
  metaLoggedTimestamp   = models.DateTimeField(auto_now_add = True)
  metaLoggingErrors     = models.TextField(blank = True)

  toObjectMetadata: Callable  # type: ignore[type-arg]

  objects: models.Manager[MetadataMixin]

  def metadataFromGrpc(self, *, grpc: RequestMetadata, errors: List[str]) -> None :
    """Change own values according to the grpc object."""
    if self._state.adding:
      # HTTP caller.
      self.metaCallerHttpRequestId = parseString(
        raw    = grpc.httpCaller.requestId,
        name   = 'metaCallerHttpRequestId',
        errors = errors,
      )
      self.metaCallerHttpSite = parseString(
        raw    = grpc.httpCaller.site,
        name   = 'metaCallerHttpSite',
        errors = errors,
      )
      self.metaCallerHttpPath = parseString(
        raw    = grpc.httpCaller.path,
        name   = 'metaCallerHttpPath',
        errors = errors,
      )
      self.metaCallerHttpPodId = parseString(
        raw    = grpc.httpCaller.podId,
        name   = 'metaCallerHttpPodId',
        errors = errors,
      )

      # User.
      self.metaUserId = parseString(
        raw    = grpc.user.id,
        name   = 'metaUserId',
        errors = errors,
      )
      self.metaUserType = User.UserType.Name(grpc.user.type)

      # Misc.
      self.metaReportedTimestamp = parseTimestamp(
        raw    = grpc.timestamp.ToDatetime(),
        name   = 'timestamp',
        errors = errors,
      )
      self.metaLoggingErrors = '\n'.join(errors)


  def metadataToGrpc(
      self, *,
      logMetadata    : LogRequestMetadata,
      requestMetadata: RequestMetadata,
  ) -> None :
    """Return a grpc object containing own values."""
    # HTTP caller.
    requestMetadata.httpCaller.requestId = self.metaCallerHttpRequestId
    requestMetadata.httpCaller.site      = self.metaCallerHttpSite
    requestMetadata.httpCaller.path      = self.metaCallerHttpPath
    requestMetadata.httpCaller.podId     = self.metaCallerHttpPodId

    # User.
    requestMetadata.user.id   = self.metaUserId
    requestMetadata.user.type = User.UserType.Value(self.metaUserType)

    # Misc.
    if self.metaReportedTimestamp:
      requestMetadata.timestamp.FromDatetime(self.metaReportedTimestamp)
    if self.metaLoggedTimestamp:
      logMetadata.loggedTimestamp.FromDatetime(self.metaLoggedTimestamp)
    logMetadata.errors = self.metaLoggingErrors


  class Meta:
    """Abstract class."""
    abstract = True


class GrpcMetadataMixin(MetadataMixin):
  """gRPC related log metadata."""

  metaCallerGrpcRequestId = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcSite      = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcApp       = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcService   = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcMethod    = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcPodId     = models.TextField(default = 'UNKNOWN')

  objects: models.Manager[GrpcMetadataMixin]


  def metadataFromGrpc(self, *, grpc: RequestMetadata, errors: List[str]) -> None :
    """Change own values according to the grpc object."""
    if self._state.adding:
      self.metaCallerGrpcRequestId = parseString(
        raw    = grpc.grpcCaller.requestId,
        name   = 'metaCallerGrpcRequestId',
        errors = errors,
      )
      self.metaCallerGrpcSite = parseString(
        raw    = grpc.grpcCaller.site,
        name   = 'metaCallerGrpcSite',
        errors = errors,
      )
      self.metaCallerGrpcApp = parseString(
        raw    = grpc.grpcCaller.app,
        name   = 'metaCallerGrpcApp',
        errors = errors,
      )
      self.metaCallerGrpcService = parseString(
        raw    = grpc.grpcCaller.service,
        name   = 'metaCallerGrpcService',
        errors = errors,
      )
      self.metaCallerGrpcMethod = parseString(
        raw    = grpc.grpcCaller.method,
        name   = 'metaCallerGrpcMethod',
        errors = errors,
      )
      self.metaCallerGrpcPodId = parseString(
        raw    = grpc.grpcCaller.podId,
        name   = 'metaCallerGrpcPodId',
        errors = errors,
      )
    # Needs to be at the end because it saves errors to the model.
    super().metadataFromGrpc(grpc = grpc, errors = errors)


  def metadataToGrpc(
      self, *,
      logMetadata    : LogRequestMetadata,
      requestMetadata: RequestMetadata,
  ) -> None :
    """Return a grpc object containing own values."""
    super().metadataToGrpc(logMetadata = logMetadata, requestMetadata = requestMetadata)

    requestMetadata.grpcCaller.requestId = self.metaCallerGrpcRequestId
    requestMetadata.grpcCaller.site      = self.metaCallerGrpcSite
    requestMetadata.grpcCaller.app       = self.metaCallerGrpcApp
    requestMetadata.grpcCaller.service   = self.metaCallerGrpcService
    requestMetadata.grpcCaller.method    = self.metaCallerGrpcMethod
    requestMetadata.grpcCaller.podId     = self.metaCallerGrpcPodId

  class Meta(MetadataMixin.Meta):
    abstract = True
