"""core-sawmill abstract logs models."""

from __future__ import annotations

# Python.
from datetime import datetime, timedelta
from typing import List, Callable

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parseUtil import parseTimestamp, parseString
from khaleesi.proto.core_pb2 import ObjectMetadata, RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import (
  LogRequestMetadata,
  ProcessedResponse,
  Response,
  ResponseRequest,
)
from microservice.models.logs.metadataMixin import MIN_TIMESTAMP


class ResponseMetadataMixin(models.Model):
  """Common metadata."""
  # Meta.
  metaResponseStatus = models.TextField(default = 'IN_PROGRESS')

  # Time.
  metaResponseReportedTimestamp = models.DateTimeField(default = MIN_TIMESTAMP)
  metaResponseLoggedTimestamp = models.DateTimeField(auto_now = True)
  metaChildDuration = models.DurationField(default = timedelta())

  # Misc.
  metaResponseLoggingErrors = models.TextField(blank = True)

  # From MetadataMixin.
  metaReportedTimestamp: datetime
  metaLoggedTimestamp  : datetime

  # From base models.
  toGrpc          : Callable  # type: ignore[type-arg]
  khaleesiSave    : Callable  # type: ignore[type-arg]
  toObjectMetadata: Callable  # type: ignore[type-arg]

  objects: models.Manager[ResponseMetadataMixin]

  @property
  def inProgress(self) -> bool :
    """Check if the request is still in progress."""
    return self.metaResponseStatus == 'IN_PROGRESS'

  @property
  def reportedDuration(self) -> timedelta :
    """Get the reported duration."""
    if self.inProgress or \
        self.metaReportedTimestamp == MIN_TIMESTAMP or \
        self.metaResponseReportedTimestamp == MIN_TIMESTAMP:
      return timedelta()
    return self.metaResponseReportedTimestamp - self.metaReportedTimestamp

  @property
  def loggedDuration(self) -> timedelta :
    """Get the logged duration."""
    if self.inProgress:
      return timedelta()
    return self.metaResponseLoggedTimestamp - self.metaLoggedTimestamp

  @property
  def childDurationRelative(self) -> float:
    """Get the child duration compared to the logged duration."""
    if self.inProgress or not self.loggedDuration:
      return 0
    return self.metaChildDuration / self.loggedDuration

  def addChildDuration(self, *, duration: timedelta) -> None :
    """Log request duration."""
    self.metaChildDuration += duration

  def finish(self, *, request: ResponseRequest) -> None :
    """Finish an in-progress HTTP request."""
    metadata = ObjectMetadata()
    grpc = self.toGrpc(metadata = metadata)
    grpc.response.CopyFrom(request.response)
    grpc.responseMetadata.CopyFrom(request.requestMetadata)
    self.khaleesiSave(metadata = metadata, grpc = grpc)

  def responseMetadataFromGrpc(
      self, *,
      metadata: RequestMetadata,
      grpc    : Response,
      errors  : List[str],
  ) -> None :
    """Change own values according to the grpc object."""
    if self.inProgress and not self._state.adding:
      self.metaResponseStatus = parseString(
        raw    = grpc.status,
        name   = 'metaResponseStatus',
        errors = errors,
      )
      self.metaResponseReportedTimestamp = parseTimestamp(
        raw    = metadata.timestamp.ToDatetime(),
        name   = 'metaResponseReportedTimestamp',
        errors = errors,
      )
      self.metaResponseLoggingErrors = '\n'.join(errors)


  def responseMetadataToGrpc(
      self, *,
      logMetadata: LogRequestMetadata,
      processed  : ProcessedResponse,
      response   : Response,
  ) -> None :
    """Return a grpc object containing own values."""
    # Response.
    response.status = self.metaResponseStatus

    # Time.
    processed.loggedDuration.FromTimedelta(self.loggedDuration)
    processed.reportedDuration.FromTimedelta(self.reportedDuration)
    processed.childDurationAbsolute.FromTimedelta(self.metaChildDuration)
    processed.childDurationRelative = self.childDurationRelative

    # Misc.
    if self.metaResponseLoggedTimestamp:
      logMetadata.loggedTimestamp.FromDatetime(self.metaResponseLoggedTimestamp)
    logMetadata.errors = self.metaResponseLoggingErrors


  class Meta:
    """Abstract class."""
    abstract = True
