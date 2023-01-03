"""Test the query logs."""

# Python.
from datetime import datetime, timedelta, timezone
from math import floor
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase, TransactionTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import ResponseRequest as GrpcQueries
from microservice.models import Query
from microservice.test_util import ModelRequestMetadataMixin


@patch('microservice.models.logs.query.Parser')
@patch('microservice.models.logs.query.parse_timestamp')
@patch('microservice.models.logs.query.parse_string', return_value = 'parsed-string')
@patch.object(Query.objects.model, 'log_metadata')
class QueryManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the query logs objects manager."""

  def test_log_queries(
      self,
      metadata: MagicMock,
      string: MagicMock,
      timestamp: MagicMock,
      sql_parser: MagicMock,
  ) -> None :
    """Test logging queries."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        metadata.reset_mock()
        string.reset_mock()
        timestamp.reset_mock()
        start = datetime.now(tz = timezone.utc)
        end = start + timedelta(days = 1)
        timestamp.side_effect = [ start, end, start, end ]
        sql_parser.reset_mock()
        sql_parser.return_value.generalize = 'generalized'
        sql_parser.return_value.tables = [ 'table1', 'table2' ]
        sql_parser.return_value.columns = []
        queries = GrpcQueries()
        queries.queries.add()
        queries.queries.add()
        request_metadata = RequestMetadata()
        self.set_request_metadata(
          request_metadata = request_metadata,
          now              = start,
          user             = user_type,
        )
        # Execute test.
        result = Query.objects.log_queries(
          queries = queries.queries,
          metadata = request_metadata,
        )
        # Assert result.
        self.assertEqual(2, len(result))
        self.assertEqual('table1,table2', result[0].tables)
        self.assertEqual(''             , result[1].columns)
        self.assertEqual(timedelta(days = 1), result[0].reported_duration)
        self.assertEqual(2, metadata.call_count)
        self.assertEqual(queries.request_metadata, metadata.call_args_list[0].kwargs['metadata'])
        self.assertEqual(queries.request_metadata, metadata.call_args_list[1].kwargs['metadata'])
        self.assertEqual([]                      , metadata.call_args_list[0].kwargs['errors'])
        self.assertEqual([]                      , metadata.call_args_list[1].kwargs['errors'])

  def test_log_queries_empty(self, *_: MagicMock) -> None :
    """Test logging queries."""
    # Execute test.
    result = Query.objects.log_queries(
      queries = GrpcQueries().queries,
      metadata = RequestMetadata(),
    )
    # Assert result.
    self.assertEqual(0, len(result))


class QueryTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the query logs models."""

  def test_to_grpc_query(self) -> None :
    """Test that general mapping to gRPC works."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        query = Query(
          query_id       = 'query-id',
          raw            = 'raw',
          normalized     = 'normalized',
          tables         = 'table1,table2',
          columns        = '',
          reported_start = datetime.now(tz = timezone.utc),
          reported_end   = datetime.now(tz = timezone.utc) + timedelta(days = 1),
          **self.model_full_request_metadata(user = user_type),
        )
        # Execute test.
        result = query.to_grpc_query_response()
        # Assert result.
        self.assert_grpc_request_metadata(
          model = query,
          grpc = result.query_request_metadata,
          grpc_response = result.query_response_metadata,
        )
        self.assertEqual(query.query_id         , result.query.id)
        self.assertEqual(query.raw              , result.query.raw)
        self.assertEqual(query.normalized       , result.normalized)
        self.assertEqual(2                      , len(result.tables))
        self.assertEqual('table1'               , result.tables[0])
        self.assertEqual('table2'               , result.tables[1])
        self.assertEqual(0                      , len(result.columns))
        self.assertEqual(
          query.reported_start.replace(tzinfo = None),  # pylint: disable=unexpected-keyword-arg
          result.query.start.ToDatetime(),
        )
        self.assertEqual(query.reported_end.replace(tzinfo = None), result.query.end.ToDatetime())  # pylint: disable=unexpected-keyword-arg
        self.assertEqual(
          floor(query.reported_duration.total_seconds()),
          result.reported_duration.seconds,
        )

  def test_empty_to_grpc_event(self) -> None :
    """Test that mapping to gRPC for empty queries works."""
    # Prepare data.
    query = Query(
      reported_start = datetime.now(tz = timezone.utc),
      reported_end = datetime.now(tz = timezone.utc) + timedelta(days = 1),
      **self.model_empty_request_metadata(),
    )
    # Execute test.
    result = query.to_grpc_query_response()
    # Assert result.
    self.assertIsNotNone(result)
