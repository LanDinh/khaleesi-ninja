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
          raw    = metadata.caller.httpRequestId,
          name   = 'metaCallerHttpRequestId',
          errors = errors,
        ),
        'metaCallerGrpcRequestId': parseString(
          raw    = metadata.caller.grpcRequestId,
          name   = 'metaCallerGrpcRequestId',
          errors = errors,
        ),
        'metaCallerKhaleesiGate': parseString(
          raw    = metadata.caller.khaleesiGate,
          name   = 'metaCallerKhaleesiGate',
          errors = errors,
        ),
        'metaCallerKhaleesiService': parseString(
          raw    = metadata.caller.khaleesiService,
          name   = 'metaCallerKhaleesiService',
          errors = errors,
        ),
        'metaCallerGrpcService': parseString(
          raw    = metadata.caller.grpcService,
          name   = 'metaCallerGrpcService',
          errors = errors,
        ),
        'metaCallerGrpcMethod': parseString(
          raw    = metadata.caller.grpcMethod,
          name   = 'metaCallerGrpcMethod',
          errors = errors,
        ),
        'metaCallerPodId': parseString(
          raw    = metadata.caller.podId,
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
    requestMetadata.caller.httpRequestId   = self.metaCallerHttpRequestId
    requestMetadata.caller.grpcRequestId   = self.metaCallerGrpcRequestId
    requestMetadata.caller.khaleesiGate    = self.metaCallerKhaleesiGate
    requestMetadata.caller.khaleesiService = self.metaCallerKhaleesiService
    requestMetadata.caller.grpcService     = self.metaCallerGrpcService
    requestMetadata.caller.grpcMethod      = self.metaCallerGrpcMethod
    requestMetadata.caller.podId           = self.metaCallerPodId
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
