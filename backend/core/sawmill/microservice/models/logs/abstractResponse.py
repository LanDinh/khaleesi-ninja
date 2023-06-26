"""core-sawmill abstract response logs models."""

# Python.
from datetime import datetime, timezone, timedelta
from typing import List

# Django.
from django.conf import settings
from django.db import models

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.parseUtil import parseTimestamp
from khaleesi.proto.core_sawmill_pb2 import (
  Response as GrpcResponse,
  ResponseMetadata as GrpcResponseMetadata,
  ProcessedResponse as GrpcProcessedResponse,
)
from microservice.models.logs.abstract import Metadata


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class ResponseMetadata(Metadata):
  """Common metadata."""

  # Meta.
  metaResponseStatus = models.TextField(default = 'IN_PROGRESS')

  # Time.
  metaResponseReportedTimestamp = models.DateTimeField(
    default = datetime.min.replace(tzinfo = timezone.utc),
  )
  metaResponseLoggedTimestamp = models.DateTimeField(auto_now = True)
  metaChildDuration = models.DurationField(default = timedelta())

  # Misc.
  metaResponseLoggingErrors = models.TextField(blank = True)

  @property
  def isInProgress(self) -> bool :
    """Check if the request is still in progress."""
    return self.metaResponseStatus == 'IN_PROGRESS'

  @property
  def reportedDuration(self) -> timedelta :
    """Get the reported duration."""
    if self.isInProgress or \
        self.metaReportedTimestamp == datetime.min.replace(tzinfo = timezone.utc) or \
        self.metaResponseReportedTimestamp == datetime.min.replace(tzinfo = timezone.utc):
      return timedelta()
    return self.metaResponseReportedTimestamp - self.metaReportedTimestamp

  @property
  def loggedDuration(self) -> timedelta :
    """Get the logged duration."""
    if self.isInProgress:
      return timedelta()
    return self.metaResponseLoggedTimestamp - self.metaLoggedTimestamp

  @property
  def childDurationRelative(self) -> float:
    """Get the child duration compared to the logged duration."""
    if self.isInProgress:
      return 0
    return self.metaChildDuration / self.loggedDuration

  def logResponse(self, *, grpcResponse: GrpcResponse) -> None :
    """Log response."""

    errors: List[str] = []

    if grpcResponse.status:
      self.metaResponseStatus = grpcResponse.status
    else:
      errors.append('Response status is missing.\n')
      self.metaResponseStatus = 'UNKNOWN'
    responseTimestamp =  parseTimestamp(
      raw    = grpcResponse.timestamp.ToDatetime(),
      name   = 'timestamp',
      errors = errors,
    )
    if responseTimestamp:
      self.metaResponseReportedTimestamp = responseTimestamp
    self.metaResponseLoggingErrors = '\n'.join(errors)

  def responseToGrpc(
      self, *,
      metadata : GrpcResponseMetadata,
      response : GrpcResponse,
      processed: GrpcProcessedResponse,
  ) -> None :
    """Fill in the request metadata for grpc."""
    # Metadata.
    metadata.loggedTimestamp.FromDatetime(self.metaResponseLoggedTimestamp)
    metadata.errors = self.metaResponseLoggingErrors
    # Response.
    response.timestamp.FromDatetime(self.metaResponseReportedTimestamp)
    response.status = self.metaResponseStatus
    # Processed data.
    processed.loggedDuration.FromTimedelta(self.loggedDuration)
    processed.reportedDuration.FromTimedelta(self.reportedDuration)
    processed.childDurationAbsolute.FromTimedelta(self.metaChildDuration)
    processed.childDurationRelative = self.childDurationRelative

  class Meta:
    """Abstract class."""
    abstract = True
