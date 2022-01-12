"""core-sawmill abstract models."""

# Python.
from datetime import datetime, timezone
from typing import Dict, Any

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import RequestMetadata
from microservice.parse_util import parse_timestamp


class Metadata(models.Model):
  """Common metadata."""

  # Caller.
  meta_caller_request_id       = models.TextField(default = 'UNKNOWN')
  meta_caller_khaleesi_gate    = models.TextField(default = 'UNKNOWN')
  meta_caller_khaleesi_service = models.TextField(default = 'UNKNOWN')
  meta_caller_grpc_service     = models.TextField(default = 'UNKNOWN')
  meta_caller_grpc_method      = models.TextField(default = 'UNKNOWN')

  # User.
  meta_user_id   = models.TextField(default = 'UNKNOWN')
  meta_user_type = models.IntegerField(default = 0)

  # Time.
  meta_event_timestamp  = models.DateTimeField(
    default = datetime.min.replace(tzinfo = timezone.utc))
  meta_logged_timestamp = models.DateTimeField(auto_now_add = True)

  # Misc.
  meta_logging_errors = models.TextField(blank = True)

  @staticmethod
  def log_metadata(*, metadata: RequestMetadata, errors: str) -> Dict[str, Any] :
    """Parse common metadata."""
    event_timestamp, event_timestamp_error = parse_timestamp(
      raw  = metadata.timestamp.ToDatetime(),
      name = 'event_timestamp',
    )
    errors += event_timestamp_error
    return {
        # Time.
        'meta_event_timestamp': event_timestamp,
        # Caller.
        'meta_caller_request_id'      : metadata.caller.request_id,
        'meta_caller_khaleesi_gate'   : metadata.caller.khaleesi_gate,
        'meta_caller_khaleesi_service': metadata.caller.khaleesi_service,
        'meta_caller_grpc_service'    : metadata.caller.grpc_service,
        'meta_caller_grpc_method'     : metadata.caller.grpc_method,
        # User.
        'meta_user_id'  : metadata.user.id,
        'meta_user_type': metadata.user.type,
        # Misc.
        'meta_logging_errors': errors,
    }

  class Meta:
    """Abstract class."""
    abstract = True
