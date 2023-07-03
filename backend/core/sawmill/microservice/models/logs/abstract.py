"""core-sawmill abstract logs models."""

# Python.
from datetime import datetime, timezone
from typing import Dict, Any, List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import ResponseMetadata
from khaleesi.core.shared.parseUtil import parseTimestamp, parseString


class Metadata(models.Model):
  """Common metadata."""

  # Caller.
  metaCallerHttpRequestId   = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcRequestId   = models.TextField(default = 'UNKNOWN')
  metaCallerKhaleesiGate    = models.TextField(default = 'UNKNOWN')
  metaCallerKhaleesiService = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcService     = models.TextField(default = 'UNKNOWN')
  metaCallerGrpcMethod      = models.TextField(default = 'UNKNOWN')
  metaCallerPodId           = models.TextField(default = 'UNKNOWN')

  # User.
  metaUserId   = models.TextField(default = 'UNKNOWN')
  metaUserType = models.IntegerField(default = 0)

  # Time.
  metaReportedTimestamp  = models.DateTimeField(
    default = datetime.min.replace(tzinfo = timezone.utc),
  )
  metaLoggedTimestamp = models.DateTimeField(auto_now_add = True)

  # Misc.
  metaLoggingErrors = models.TextField(blank = True)

  @staticmethod
  def logMetadata(*, metadata: RequestMetadata, errors: List[str]) -> Dict[str, Any] :
    """Parse common metadata."""
    return {
        # Caller.
        'metaCallerHttpRequestId': parseString(
          raw    = metadata.grpcCaller.requestId,
          name   = 'metaCallerHttpRequestId',
          errors = errors,
        ),
        'metaCallerGrpcRequestId': parseString(
          raw    = metadata.grpcCaller.requestId,
          name   = 'metaCallerGrpcRequestId',
          errors = errors,
        ),
        'metaCallerKhaleesiGate': parseString(
          raw    = metadata.grpcCaller.khaleesiGate,
          name   = 'metaCallerKhaleesiGate',
          errors = errors,
        ),
        'metaCallerKhaleesiService': parseString(
          raw    = metadata.grpcCaller.khaleesiService,
          name   = 'metaCallerKhaleesiService',
          errors = errors,
        ),
        'metaCallerGrpcService': parseString(
          raw    = metadata.grpcCaller.grpcService,
          name   = 'metaCallerGrpcService',
          errors = errors,
        ),
        'metaCallerGrpcMethod': parseString(
          raw    = metadata.grpcCaller.grpcMethod,
          name   = 'metaCallerGrpcMethod',
          errors = errors,
        ),
        'metaCallerPodId': parseString(
          raw    = metadata.grpcCaller.podId,
          name   = 'metaCallerPodId',
          errors = errors,
        ),
        # User.
        'metaUserId': parseString(raw = metadata.user.id, name = 'metaUserId', errors = errors),
        'metaUserType': metadata.user.type,
        # Time.
        'metaReportedTimestamp': parseTimestamp(
          raw    = metadata.timestamp.ToDatetime(),
          name   = 'timestamp',
          errors = errors,
        ),
        # Misc.
        'metaLoggingErrors': '\n'.join(errors),
    }

  def requestMetadataToGrpc(self, *, requestMetadata: RequestMetadata) -> None :
    """Fill in the request metadata for grpc."""
    # Caller.
    requestMetadata.httpCaller.requestId       = self.metaCallerHttpRequestId
    requestMetadata.grpcCaller.requestId       = self.metaCallerGrpcRequestId
    requestMetadata.grpcCaller.khaleesiGate    = self.metaCallerKhaleesiGate
    requestMetadata.grpcCaller.khaleesiService = self.metaCallerKhaleesiService
    requestMetadata.grpcCaller.grpcService     = self.metaCallerGrpcService
    requestMetadata.grpcCaller.grpcMethod      = self.metaCallerGrpcMethod
    requestMetadata.grpcCaller.podId           = self.metaCallerPodId
    # User.
    requestMetadata.user.id   = self.metaUserId
    requestMetadata.user.type = self.metaUserType  # type: ignore[assignment]
    # Time.
    requestMetadata.timestamp.FromDatetime(self.metaReportedTimestamp)

  def responseMetadataToGrpc(self, *, responseMetadata: ResponseMetadata) -> None :
    """Fill in the request metadata for grpc."""
    responseMetadata.loggedTimestamp.FromDatetime(self.metaLoggedTimestamp)
    responseMetadata.errors = self.metaLoggingErrors

  class Meta:
    """Abstract class."""
    abstract = True
    ordering = [ 'pk' ]
