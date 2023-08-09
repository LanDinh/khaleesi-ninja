"""Db query logs."""

from __future__ import annotations

# Python.
from datetime import timedelta
from typing import List

# Django.
from django.db import models

# 3rd party.
from sql_metadata import Parser  # type: ignore[import]

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.models.baseModel import Manager
from khaleesi.core.models.idModel import Model
from khaleesi.core.shared.parseUtil import parseString, parseTimestamp
from khaleesi.proto.core_pb2 import ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import QueryRequest as GrpcQueryRequest
from microservice.models.logs.metadataMixin import GrpcMetadataMixin, MIN_TIMESTAMP


class Query(Model[GrpcQueryRequest], GrpcMetadataMixin):
  """Query logs."""
  khaleesiId = models.TextField(unique = False, editable = False)  # Avoid index building.

  reportedStart = models.DateTimeField()
  reportedEnd   = models.DateTimeField()

  raw        = models.TextField(default = 'UNKNOWN')
  normalized = models.TextField(default = 'UNKNOWN')
  tables     = models.TextField(default = 'UNKNOWN')
  columns    = models.TextField(default = 'UNKNOWN')

  objects: Manager[Query]  # type: ignore[assignment]

  @property
  def reportedDuration(self) -> timedelta :
    """Report query duration."""
    if not self.reportedStart or not self.reportedEnd or \
        MIN_TIMESTAMP in (self.reportedStart, self.reportedEnd):
      return timedelta()
    return self.reportedEnd - self.reportedStart

  def khaleesiSave(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcQueryRequest,
      dbSave  : bool = True,
  ) -> None :
    """Change own values according to the grpc object."""
    errors: List[str] = []

    if self._state.adding:
      self.reportedStart = parseTimestamp(
        raw    = grpc.query.start.ToDatetime(),
        name   = 'start',
        errors = errors,
      )
      self.reportedEnd = parseTimestamp(
        raw    = grpc.query.end.ToDatetime(),
        name   = 'end',
        errors = errors,
      )

      raw = parseString(raw = grpc.query.raw, name = 'raw', errors = errors)
      self.raw = raw
      try:
        parser = Parser(sql = raw)
        self.normalized = parser.generalize
        self.tables  = ','.join(parser.tables)
        self.columns = ','.join(parser.columns)
      except ValueError:  # TODO(46) - sql-metadata doesn't support all query types.  # pylint: disable=line-too-long  # pragma: no cover
        LOGGER.error(f'ValueError when parsing SQL: {raw}')

    # Needs to be at the end because it saves errors to the model.
    self.metadataFromGrpc(grpc = grpc.requestMetadata, errors = errors)
    super().khaleesiSave(metadata = metadata, grpc = grpc, dbSave = dbSave)

  def toGrpc(self) -> GrpcQueryRequest :
    """Return a grpc object containing own values."""
    grpc = GrpcQueryRequest()
    self.metadataToGrpc(logMetadata = grpc.logMetadata, requestMetadata = grpc.requestMetadata)

    if self.reportedStart:
      grpc.query.start.FromDatetime(self.reportedStart)
    if self.reportedEnd:
      grpc.query.end.FromDatetime(self.reportedEnd)
    grpc.query.reportedDuration.FromTimedelta(self.reportedDuration)

    grpc.query.raw  = self.raw
    grpc.query.normalized = self.normalized
    for table in self.tables.split(','):
      if table:
        grpc.query.tables.append(table)
    for column in self.columns.split(','):
      if column:
        grpc.query.columns.append(column)

    return grpc
