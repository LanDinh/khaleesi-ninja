"""core-sawmill abstract logs models."""

# Python.
from datetime import datetime, timezone
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parseUtil import parseTimestamp, parseString
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import LogRequestMetadata


class MetadataMixin(models.Model):
  """Common metadata."""

  # HTTP caller.
  metaCallerHttpRequestId    = models.TextField(default = 'UNKNOWN')
  metaCallerHttpKhaleesiGate = models.TextField(default = 'UNKNOWN')
  metaCallerHttpPath         = models.TextField(default = 'UNKNOWN')
  metaCallerHttpPodId        = models.TextField(default = 'UNKNOWN')

  # User.
  metaUserId   = models.TextField(default = 'UNKNOWN')
  metaUserType = models.TextField(default = 'UNKNOWN')

  # Misc.
  metaReportedTimestamp  = models.DateTimeField(
    default = datetime.min.replace(tzinfo = timezone.utc),
  )
  metaLoggedTimestamp = models.DateTimeField(auto_now_add = True)
  metaLoggingErrors   = models.TextField(blank = True)

  def metadataFromGrpc(self, *, grpc: RequestMetadata, errors: List[str]) -> None :
    """Change own values according to the grpc object."""
    if self._state.adding:
      # HTTP caller.
      self.metaCallerHttpRequestId = parseString(
        raw    = grpc.httpCaller.requestId,
        name   = 'metaCallerHttpRequestId',
        errors = errors,
      )
      self.metaCallerHttpKhaleesiGate = parseString(
        raw    = grpc.httpCaller.khaleesiGate,
        name   = 'metaCallerHttpKhaleesiGate',
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
    requestMetadata.httpCaller.requestId    = self.metaCallerHttpRequestId
    requestMetadata.httpCaller.khaleesiGate = self.metaCallerHttpKhaleesiGate
    requestMetadata.httpCaller.path         = self.metaCallerHttpPath
    requestMetadata.httpCaller.podId        = self.metaCallerHttpPodId

    # User.
    requestMetadata.user.id   = self.metaUserId
    requestMetadata.user.type = User.UserType.Value(self.metaUserType)

    # Misc.
    requestMetadata.timestamp.FromDatetime(self.metaReportedTimestamp)
    logMetadata.loggedTimestamp.FromDatetime(self.metaLoggedTimestamp)
    logMetadata.errors = self.metaLoggingErrors


  class Meta:
    """Abstract class."""
    abstract = True


class GrpcMetadataMixin(MetadataMixin):
  """gRPC related log metadata."""

  metaCallerGrpcRequestId       = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcKhaleesiGate    = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcKhaleesiService = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcGrpcService     = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcGrpcMethod      = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcPodId           = models.TextField(default = 'UNKNOWN')


  def metadataFromGrpc(self, *, grpc: RequestMetadata, errors: List[str]) -> None :
    """Change own values according to the grpc object."""
    if not self._state.adding:
      self.metaCallerGrpcRequestId = parseString(
        raw    = grpc.grpcCaller.requestId,
        name   = 'metaCallerGrpcRequestId',
        errors = errors,
      )
      self.metaCallerGrpcKhaleesiGate = parseString(
        raw    = grpc.grpcCaller.khaleesiGate,
        name   = 'metaCallerKhaleesiGate',
        errors = errors,
      )
      self.metaCallerGrpcKhaleesiService = parseString(
        raw    = grpc.grpcCaller.khaleesiService,
        name   = 'metaCallerKhaleesiService',
        errors = errors,
      )
      self.metaCallerGrpcGrpcService = parseString(
        raw    = grpc.grpcCaller.grpcService,
        name   = 'metaCallerGrpcService',
        errors = errors,
      )
      self.metaCallerGrpcGrpcMethod = parseString(
        raw    = grpc.grpcCaller.grpcMethod,
        name   = 'metaCallerGrpcMethod',
        errors = errors,
      )
      self.metaCallerGrpcPodId = parseString(
        raw    = grpc.grpcCaller.podId,
        name   = 'metaCallerPodId',
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

    requestMetadata.grpcCaller.requestId       = self.metaCallerGrpcRequestId
    requestMetadata.grpcCaller.khaleesiGate    = self.metaCallerGrpcKhaleesiGate
    requestMetadata.grpcCaller.khaleesiService = self.metaCallerGrpcKhaleesiService
    requestMetadata.grpcCaller.grpcService     = self.metaCallerGrpcGrpcService
    requestMetadata.grpcCaller.grpcMethod      = self.metaCallerGrpcGrpcMethod
    requestMetadata.grpcCaller.podId           = self.metaCallerGrpcPodId

  class Meta(MetadataMixin.Meta):
    abstract = True
