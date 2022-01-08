"""core-sawmill abstract models."""

# Python.
from datetime import datetime, timezone
from typing import Dict, Any

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_sawmill_pb2 import Metadata as GrpcMetadata
from microservice.parse_util import parse_timestamp


class Metadata(models.Model):
  """Common metadata."""

  # Time.
  meta_event_timestamp  = models.DateTimeField(
      default = datetime.min.replace(tzinfo = timezone.utc))
  meta_logged_timestamp = models.DateTimeField(auto_now_add = True)

  # Logger.
  meta_logger_request_id       = models.TextField(default = 'UNKNOWN')
  meta_logger_khaleesi_gate    = models.TextField(default = 'UNKNOWN')
  meta_logger_khaleesi_service = models.TextField(default = 'UNKNOWN')
  meta_logger_grpc_service     = models.TextField(default = 'UNKNOWN')
  meta_logger_grpc_method      = models.TextField(default = 'UNKNOWN')

  # Misc.
  meta_logging_errors = models.TextField(blank = True)

  @staticmethod
  def log_metadata(*, metadata: GrpcMetadata, errors: str) -> Dict[str, Any] :
    """Parse common metadata."""
    event_timestamp, event_timestamp_error = parse_timestamp(
      raw = metadata.timestamp.ToDatetime(),
      name = 'event_timestamp',
    )
    errors += event_timestamp_error
    return {
        # Time.
        'meta_event_timestamp': event_timestamp,
        # Logger.
        'meta_logger_request_id'      : metadata.logger.request_id,
        'meta_logger_khaleesi_gate'   : metadata.logger.khaleesi_gate,
        'meta_logger_khaleesi_service': metadata.logger.khaleesi_service,
        'meta_logger_grpc_service'    : metadata.logger.grpc_service,
        'meta_logger_grpc_method'     : metadata.logger.grpc_method,
        # Misc.
        'meta_logging_errors': errors,
    }

  class Meta:
    """Abstract class."""
    abstract = True
