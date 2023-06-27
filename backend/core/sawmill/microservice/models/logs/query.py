"""Db query logs."""

# Python.
from __future__ import annotations
from datetime import timedelta, datetime, timezone
from typing import List

# Django.
from django.db import models

# gRPC.
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer

# 3rd party.
from sql_metadata import Parser  # type: ignore[import]

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.parseUtil import parseString, parseTimestamp
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import Query as GrpcQuery, QueryResponse as GrpcQueryResponse
from microservice.models.logs.abstract import Metadata


class QueryManager(models.Manager['Query']):
  """Custom model manager."""

  def logQueries(
      self, *,
      queries : RepeatedCompositeFieldContainer[GrpcQuery],
      metadata: RequestMetadata,
  ) -> List[Query] :
    """Log queries."""
    newQueries: List[Query] = []
    for grpcQuery in queries:
      errors: List[str] = []
      raw    = parseString(raw = grpcQuery.raw, name = 'raw', errors = errors)
      parser = Parser(sql = raw)
      try:
        query = Query(  # type: ignore[misc]
          queryId    = parseString(raw = grpcQuery.id, name = 'queryId', errors = errors),
          connection = parseString(
            raw    = grpcQuery.connection,
            name   = 'connection',
            errors = errors,
          ),
          raw           = raw,
          normalized    = parser.generalize,
          tables        = ','.join(parser.tables),
          columns       = ','.join(parser.columns),
          reportedStart = parseTimestamp(
            raw    = grpcQuery.start.ToDatetime(),
            name   = 'start',
            errors = errors,
          ),
          reportedEnd = parseTimestamp(
            raw    = grpcQuery.end.ToDatetime(),
            name   = 'end',
            errors = errors,
          ),
          **self.model.logMetadata(metadata = metadata, errors = errors)
        )
        newQueries.append(query)
      except ValueError:  # TODO(46) - sql-metadata doesn't support all query types.  # pylint: disable=line-too-long  # pragma: no cover
        LOGGER.error(f'ValueError when parsing SQL: {raw}')
    return self.bulk_create(objs = newQueries, batch_size = 100)


class Query(Metadata):
  """Query logs."""
  queryId    = models.TextField(default = 'UNKNOWN')
  connection = models.TextField(default = 'UNKNOWN')

  raw        = models.TextField(default = 'UNKNOWN')
  normalized = models.TextField(default = 'UNKNOWN')

  tables  = models.TextField(default = 'UNKNOWN')
  columns = models.TextField(default = 'UNKNOWN')

  reportedStart = models.DateTimeField()
  reportedEnd   = models.DateTimeField()

  objects = QueryManager()

  @property
  def reportedDuration(self) -> timedelta :
    """Report query duration."""
    if self.reportedEnd == datetime.max.replace(tzinfo = timezone.utc):
      return self.metaReportedTimestamp - self.reportedStart
    return self.reportedEnd - self.reportedStart

  def toGrpc(self) -> GrpcQueryResponse :
    """Map to gRPC query message."""

    grpcQueryResponse = GrpcQueryResponse()
    self.requestMetadataToGrpc(requestMetadata = grpcQueryResponse.queryRequestMetadata)
    self.responseMetadataToGrpc(responseMetadata = grpcQueryResponse.queryResponseMetadata)
    grpcQueryResponse.query.id         = self.queryId
    grpcQueryResponse.query.connection = self.connection
    grpcQueryResponse.query.raw        = self.raw
    grpcQueryResponse.normalized       = self.normalized
    grpcQueryResponse.query.start.FromDatetime(self.reportedStart)
    grpcQueryResponse.query.end.FromDatetime(self.reportedEnd)
    grpcQueryResponse.reportedDuration.FromTimedelta(self.reportedDuration)
    for table in self.tables.split(','):
      if table:
        grpcQueryResponse.tables.append(table)
    for column in self.columns.split(','):
      if column:
        grpcQueryResponse.columns.append(column)

    return grpcQueryResponse
