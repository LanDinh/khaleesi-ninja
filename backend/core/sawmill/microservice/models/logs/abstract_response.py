"""core-sawmill abstract response logs models."""

# Python.
from datetime import datetime, timezone, timedelta
from typing import List

# Django.
from django.conf import settings
from django.db import models

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.parse_util import parse_timestamp
from khaleesi.proto.core_sawmill_pb2 import (
  Response as GrpcResponse,
  ResponseMetadata as GrpcResponseMetadata,
  ProcessedResponse as GrpcProcessedResponse,
)
from microservice.models.logs.abstract import Metadata


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class ResponseMetadata(Metadata):
  """Common metadata."""

  # Meta.
  meta_response_status = models.TextField(default = 'IN_PROGRESS')

  # Time.
  meta_response_reported_timestamp = models.DateTimeField(
    default = datetime.min.replace(tzinfo = timezone.utc),
  )
  meta_response_logged_timestamp = models.DateTimeField(auto_now = True)
  meta_child_duration = models.DurationField(default = timedelta())

  # Misc.
  meta_response_logging_errors = models.TextField(blank = True)

  @property
  def is_in_progress(self) -> bool :
    """Check if the request is still in progress."""
    return self.meta_response_status == 'IN_PROGRESS'

  @property
  def reported_duration(self) -> timedelta :
    """Get the reported duration."""
    if self.is_in_progress or \
        self.meta_reported_timestamp == datetime.min.replace(tzinfo = timezone.utc) or \
        self.meta_response_reported_timestamp == datetime.min.replace(tzinfo = timezone.utc):
      return timedelta()
    return self.meta_response_reported_timestamp - self.meta_reported_timestamp

  @property
  def logged_duration(self) -> timedelta :
    """Get the logged duration."""
    if self.is_in_progress:
      return timedelta()
    return self.meta_response_logged_timestamp - self.meta_logged_timestamp

  @property
  def child_duration_relative(self) -> float:
    """Get the child duration compared to the logged duration."""
    if self.is_in_progress:
      return 0
    return self.meta_child_duration / self.logged_duration

  def log_response(self, *, grpc_response: GrpcResponse) -> None :
    """Log response."""

    errors: List[str] = []

    if grpc_response.status:
      self.meta_response_status = grpc_response.status
    else:
      errors.append('Response status is missing.\n')
      self.meta_response_status = 'UNKNOWN'
    response_timestamp =  parse_timestamp(
      raw    = grpc_response.timestamp.ToDatetime(),
      name   = 'timestamp',
      errors = errors,
    )
    if response_timestamp:
      self.meta_response_reported_timestamp = response_timestamp
    self.meta_response_logging_errors = '\n'.join(errors)

  def response_to_grpc(
      self, *,
      metadata: GrpcResponseMetadata,
      response: GrpcResponse,
      processed: GrpcProcessedResponse,
  ) -> None :
    """Fill in the request metadata for grpc."""
    # Metadata.
    metadata.logged_timestamp.FromDatetime(self.meta_response_logged_timestamp)
    metadata.errors = self.meta_response_logging_errors
    # Response.
    response.timestamp.FromDatetime(self.meta_response_reported_timestamp)
    response.status = self.meta_response_status
    # Processed data.
    processed.logged_duration.FromTimedelta(self.logged_duration)
    processed.reported_duration.FromTimedelta(self.reported_duration)
    processed.child_duration_absolute.FromTimedelta(self.meta_child_duration)
    processed.child_duration_relative = self.child_duration_relative

  class Meta:
    """Abstract class."""
    abstract = True
