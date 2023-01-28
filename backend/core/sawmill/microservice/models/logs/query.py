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
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import Query as GrpcQuery, QueryResponse as GrpcQueryResponse
from microservice.models.logs.abstract import Metadata
from microservice.parse_util import parse_string, parse_timestamp


class QueryManager(models.Manager['Query']):
  """Custom model manager."""

  def log_queries(
      self, *,
      queries: RepeatedCompositeFieldContainer[GrpcQuery],
      metadata: RequestMetadata,
  ) -> List[Query] :
    """Log queries."""
    new_queries: List[Query] = []
    for grpc_query in queries:
      errors: List[str] = []
      raw = parse_string(raw = grpc_query.raw, name = 'raw', errors = errors)
      parser = Parser(sql = raw)
      try:
        query = Query(  # type: ignore[misc]
          query_id       = parse_string(raw = grpc_query.id, name = 'query_id', errors = errors),
          connection     = parse_string(
            raw = grpc_query.connection,
            name = 'connection',
            errors = errors,
          ),
          raw            = raw,
          normalized     = parser.generalize,
          tables         = ','.join(parser.tables),
          columns        = ','.join(parser.columns),
          reported_start = parse_timestamp(
            raw = grpc_query.start.ToDatetime(),
            name = 'start',
            errors = errors,
          ),
          reported_end = parse_timestamp(
            raw = grpc_query.end.ToDatetime(),
            name = 'end',
            errors = errors,
          ),
          **self.model.log_metadata(metadata = metadata, errors = errors)
        )
        new_queries.append(query)
      except ValueError:  # TODO(46) - sql-metadata doesn't support all query types.
        LOGGER.error(f'ValueError when parsing SQL: {raw}')
    return self.bulk_create(objs = new_queries, batch_size = 100)


class Query(Metadata):
  """Query logs."""
  query_id   = models.TextField(default = 'UNKNOWN')
  connection = models.TextField(default = 'UNKNOWN')

  raw        = models.TextField(default = 'UNKNOWN')
  normalized = models.TextField(default = 'UNKNOWN')

  tables  = models.TextField(default = 'UNKNOWN')
  columns = models.TextField(default = 'UNKNOWN')

  reported_start = models.DateTimeField()
  reported_end = models.DateTimeField()

  objects = QueryManager()

  @property
  def reported_duration(self) -> timedelta :
    """Report query duration."""
    if self.reported_end == datetime.max.replace(tzinfo = timezone.utc):
      return self.meta_reported_timestamp - self.reported_start
    return self.reported_end - self.reported_start

  def to_grpc_query_response(self) -> GrpcQueryResponse :
    """Map to gRPC query message."""

    grpc_query_response = GrpcQueryResponse()
    self.request_metadata_to_grpc(request_metadata = grpc_query_response.query_request_metadata)
    self.response_metadata_to_grpc(response_metadata = grpc_query_response.query_response_metadata)
    grpc_query_response.query.id         = self.query_id
    grpc_query_response.query.connection = self.connection
    grpc_query_response.query.raw        = self.raw
    grpc_query_response.normalized       = self.normalized
    grpc_query_response.query.start.FromDatetime(self.reported_start)
    grpc_query_response.query.end.FromDatetime(self.reported_end)
    grpc_query_response.reported_duration.FromTimedelta(self.reported_duration)
    for table in self.tables.split(','):
      if table:
        grpc_query_response.tables.append(table)
    for column in self.columns.split(','):
      if column:
        grpc_query_response.columns.append(column)

    return grpc_query_response
