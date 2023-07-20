"""Test the query logs."""

# Python.
from datetime import datetime, timedelta, timezone
from math import floor
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.grpc import GrpcTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase, TransactionTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import ResponseRequest as GrpcGrpcQueries
from microservice.models import Query
from microservice.testUtil import ModelRequestMetadataMixin


@patch('microservice.models.logs.query.Parser')
@patch('microservice.models.logs.query.parseTimestamp')
@patch('microservice.models.logs.query.parseString', return_value = 'parsed-string')
@patch.object(Query.objects.model, 'logMetadata')
class QueryManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the query logs objects manager."""

  def testLogQueries(
      self,
      metadata : MagicMock,
      string   : MagicMock,
      timestamp: MagicMock,
      sqlParser: MagicMock,
  ) -> None :
    """Test logging queries."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        metadata.reset_mock()
        string.reset_mock()
        timestamp.reset_mock()
        start = datetime.now(tz = timezone.utc)
        end   = start + timedelta(days = 1)
        metadata.return_value = { 'metaReportedTimestamp': start }
        timestamp.side_effect = [ start, end, start, datetime.max.replace(tzinfo = timezone.utc) ]
        sqlParser.reset_mock()
        sqlParser.return_value.generalize = 'generalized'
        sqlParser.return_value.tables     = [ 'table1', 'table2' ]
        sqlParser.return_value.columns    = []
        queries = GrpcGrpcQueries()
        queries.queries.add()
        queries.queries.add()
        requestMetadata = RequestMetadata()
        self.setRequestMetadata(
          requestMetadata = requestMetadata,
          now             = start,
          user            = userType,
        )
        # Execute test.
        result = Query.objects.logQueries(queries = queries.queries, metadata = requestMetadata)
        # Assert result.
        self.assertEqual(2, len(result))
        self.assertEqual('table1,table2', result[0].tables)
        self.assertEqual(''             , result[1].columns)
        self.assertEqual(timedelta(days = 1), result[0].reportedDuration)
        self.assertEqual(timedelta(0)       , result[1].reportedDuration)
        self.assertEqual(2, metadata.call_count)
        self.assertEqual(requestMetadata, metadata.call_args_list[0].kwargs['metadata'])
        self.assertEqual(requestMetadata, metadata.call_args_list[1].kwargs['metadata'])
        self.assertEqual([]             , metadata.call_args_list[0].kwargs['errors'])
        self.assertEqual([]             , metadata.call_args_list[1].kwargs['errors'])

  def testLogQueriesEmpty(self, *_: MagicMock) -> None :
    """Test logging queries."""
    # Execute test.
    result = Query.objects.logQueries(
      queries  = GrpcGrpcQueries().queries,
      metadata = RequestMetadata(),
    )
    # Assert result.
    self.assertEqual(0, len(result))


class QueryTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the query logs models."""

  def testToGrpcQuery(self) -> None :
    """Test that general mapping to gRPC works."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        query = Query(
          queryId       = 'query-id',
          connection    = 'connection',
          raw           = 'raw',
          normalized    = 'normalized',
          tables        = 'table1,table2',
          columns       = '',
          reportedStart = datetime.now(tz = timezone.utc),
          reportedEnd   = datetime.now(tz = timezone.utc) + timedelta(days = 1),
          **self.modelFullRequestMetadata(user = userType),
        )
        # Execute test.
        result = query.toGrpc()
        # Assert result.
        self.assertGrpcRequestMetadata(
          model        = query,
          grpc         = result.queryRequestMetadata,
          grpcResponse = result.queryResponseMetadata,
        )
        self.assertEqual(query.queryId   , result.query.id)
        self.assertEqual(query.connection, result.query.connection)
        self.assertEqual(query.raw       , result.query.raw)
        self.assertEqual(query.normalized, result.normalized)
        self.assertEqual(2               , len(result.tables))
        self.assertEqual('table1'        , result.tables[0])
        self.assertEqual('table2'        , result.tables[1])
        self.assertEqual(0               , len(result.columns))
        self.assertEqual(
          query.reportedStart.replace(tzinfo = None),  # pylint: disable=unexpected-keyword-arg
          result.query.start.ToDatetime(),
        )
        self.assertEqual(query.reportedEnd.replace(tzinfo = None), result.query.end.ToDatetime())  # pylint: disable=unexpected-keyword-arg
        self.assertEqual(
          floor(query.reportedDuration.total_seconds()),
          result.reportedDuration.seconds,
        )

  def testEmptyToGrpcQuery(self) -> None :
    """Test that mapping to gRPC for empty queries works."""
    # Prepare data.
    query = Query(
      reportedStart = datetime.now(tz = timezone.utc),
      reportedEnd   = datetime.now(tz = timezone.utc) + timedelta(days = 1),
      **self.modelEmptyRequestMetadata(),
    )
    # Execute test.
    result = query.toGrpc()
    # Assert result.
    self.assertIsNotNone(result)
