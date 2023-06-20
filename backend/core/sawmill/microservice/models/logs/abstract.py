"""core-sawmill abstract logs models."""

# Python.
from datetime import datetime, timezone
from typing import Dict, Any, List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import ResponseMetadata
from khaleesi.core.shared.parse_util import parse_timestamp, parse_string


class Metadata(models.Model):
  """Common metadata."""

  # Caller.
  meta_caller_http_request_id  = models.TextField(default = 'UNKNOWN')
  meta_caller_grpc_request_id  = models.TextField(default = 'UNKNOWN')
  meta_caller_khaleesi_gate    = models.TextField(default = 'UNKNOWN')
  meta_caller_khaleesi_service = models.TextField(default = 'UNKNOWN')
  meta_caller_grpc_service     = models.TextField(default = 'UNKNOWN')
  meta_caller_grpc_method      = models.TextField(default = 'UNKNOWN')
  meta_caller_pod_id           = models.TextField(default = 'UNKNOWN')

  # User.
  meta_user_id   = models.TextField(default = 'UNKNOWN')
  meta_user_type = models.IntegerField(default = 0)

  # Time.
  meta_reported_timestamp  = models.DateTimeField(
    default = datetime.min.replace(tzinfo = timezone.utc))
  meta_logged_timestamp = models.DateTimeField(auto_now_add = True)

  # Misc.
  meta_logging_errors = models.TextField(blank = True)

  @staticmethod
  def log_metadata(*, metadata: RequestMetadata, errors: List[str]) -> Dict[str, Any] :
    """Parse common metadata."""
    return {
        # Caller.
        'meta_caller_http_request_id': parse_string(
          raw    = metadata.caller.httpRequestId,
          name   = 'meta_caller_http_request_id',
          errors = errors,
        ),
        'meta_caller_grpc_request_id': parse_string(
          raw    = metadata.caller.grpcRequestId,
          name   = 'meta_caller_grpc_request_id',
          errors = errors,
        ),
        'meta_caller_khaleesi_gate': parse_string(
          raw    = metadata.caller.khaleesiGate,
          name   = 'meta_caller_khaleesi_gate',
          errors = errors,
        ),
        'meta_caller_khaleesi_service': parse_string(
          raw    = metadata.caller.khaleesiService,
          name   = 'meta_caller_khaleesi_service',
          errors = errors,
        ),
        'meta_caller_grpc_service': parse_string(
          raw    = metadata.caller.grpcService,
          name   = 'meta_caller_grpc_service',
          errors = errors,
        ),
        'meta_caller_grpc_method': parse_string(
          raw    = metadata.caller.grpcMethod,
          name   = 'meta_caller_grpc_method',
          errors = errors,
        ),
        'meta_caller_pod_id': parse_string(
          raw    = metadata.caller.podId,
          name   = 'meta_caller_pod_id',
          errors = errors,
        ),
        # User.
        'meta_user_id': parse_string(
          raw  = metadata.user.id,
          name = 'meta_user_id',
          errors = errors,
        ),
        'meta_user_type': metadata.user.type,
        # Time.
        'meta_reported_timestamp': parse_timestamp(
          raw    = metadata.timestamp.ToDatetime(),
          name   = 'timestamp',
          errors = errors,
        ),
        # Misc.
        'meta_logging_errors': '\n'.join(errors),
    }

  def request_metadata_to_grpc(self, *, request_metadata: RequestMetadata) -> None :
    """Fill in the request metadata for grpc."""
    # Caller.
    request_metadata.caller.httpRequestId   = self.meta_caller_http_request_id
    request_metadata.caller.grpcRequestId   = self.meta_caller_grpc_request_id
    request_metadata.caller.khaleesiGate    = self.meta_caller_khaleesi_gate
    request_metadata.caller.khaleesiService = self.meta_caller_khaleesi_service
    request_metadata.caller.grpcService     = self.meta_caller_grpc_service
    request_metadata.caller.grpcMethod      = self.meta_caller_grpc_method
    request_metadata.caller.podId           = self.meta_caller_pod_id
    # User.
    request_metadata.user.id   = self.meta_user_id
    request_metadata.user.type = self.meta_user_type  # type: ignore[assignment]
    # Time.
    request_metadata.timestamp.FromDatetime(self.meta_reported_timestamp)

  def response_metadata_to_grpc(self, *, response_metadata: ResponseMetadata) -> None :
    """Fill in the request metadata for grpc."""
    response_metadata.loggedTimestamp.FromDatetime(self.meta_logged_timestamp)
    response_metadata.errors = self.meta_logging_errors

  class Meta:
    """Abstract class."""
    abstract = True
    ordering = [ 'pk' ]
