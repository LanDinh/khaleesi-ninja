"""Test the query logs."""

# Python.
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import QueryRequest as GrpcQueryRequest
from microservice.models import Query
from microservice.models.logs.metadataMixin import MIN_TIMESTAMP


class QueryTestCase(SimpleTestCase):
  """Test the query logs models."""

  def testReportedDurationEmptyStart(self) -> None :
    """Test calculating the duration."""
    # Prepare data.
    instance = Query()
    instance.reportedEnd = datetime.now(tz = timezone.utc)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testReportedDurationEmptyEnd(self) -> None :
    """Test calculating the duration."""
    # Prepare data.
    instance = Query()
    instance.reportedStart = datetime.now(tz = timezone.utc)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testReportedDurationMinStart(self) -> None :
    """Test calculating the duration."""
    # Prepare data.
    instance = Query()
    instance.reportedStart = MIN_TIMESTAMP
    instance.reportedEnd   = datetime.now(tz = timezone.utc)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testReportedDurationMinEnd(self) -> None :
    """Test calculating the duration."""
    # Prepare data.
    instance = Query()
    instance.reportedStart = datetime.now(tz = timezone.utc)
    instance.reportedEnd   = MIN_TIMESTAMP
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testReportedDuration(self) -> None :
    """Test calculating the duration."""
    # Prepare data.
    delta = timedelta(hours = 13)
    instance = Query()
    instance.reportedStart = datetime.now(tz = timezone.utc)
    instance.reportedEnd   = instance.reportedStart + delta
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(delta, result)

  @patch('microservice.models.logs.query.parseTimestamp')
  @patch('microservice.models.logs.query.parseString')
  @patch('microservice.models.logs.query.Model.khaleesiSave')
  @patch('microservice.models.logs.query.Query.metadataFromGrpc')
  @patch('microservice.models.logs.query.Parser')
  def testKhaleesiSaveNew(
      self,
      parser   : MagicMock,
      metadata : MagicMock,
      parent   : MagicMock,
      string   : MagicMock,
      timestamp: MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    # Prepare data.
    instance               = Query()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = self._createGrpcQuery(string = string, timestamp = timestamp)
    parser.return_value.generalize = 'new-normalized'
    parser.return_value.tables     = [ 'new-table1' ]
    parser.return_value.columns    = [ 'new-column1', 'new-column2' ]
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parser.assert_called_once()
    metadata.assert_called_once()
    parent.assert_called_once()
    self.assertEqual('new-normalized'         , instance.normalized)
    self.assertEqual('new-table1'             , instance.tables)
    self.assertEqual('new-column1,new-column2', instance.columns)

  @patch('microservice.models.logs.query.parseTimestamp')
  @patch('microservice.models.logs.query.parseString')
  @patch('microservice.models.logs.query.Model.khaleesiSave')
  @patch('microservice.models.logs.query.Query.metadataFromGrpc')
  @patch('microservice.models.logs.query.Parser')
  def testKhaleesiSaveOld(
      self,
      parser   : MagicMock,
      metadata : MagicMock,
      parent   : MagicMock,
      string   : MagicMock,
      timestamp: MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    # Prepare data.
    instance               = Query()
    instance._state.adding = False  # pylint: disable=protected-access
    grpc = self._createGrpcQuery(string = string, timestamp = timestamp)
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parser.assert_not_called()
    metadata.assert_called_once()
    parent.assert_called_once()
    self.assertNotEqual(
      grpc.query.start.ToDatetime().replace(tzinfo = timezone.utc),
      instance.reportedStart,
    )
    self.assertNotEqual(
      grpc.query.end.ToDatetime().replace(tzinfo = timezone.utc),
      instance.reportedEnd,
    )
    self.assertNotEqual('', instance.normalized)
    self.assertNotEqual('', instance.tables)
    self.assertNotEqual('', instance.columns)

  @patch('microservice.models.logs.query.parseTimestamp')
  @patch('microservice.models.logs.query.parseString')
  @patch('microservice.models.logs.query.Model.khaleesiSave')
  @patch('microservice.models.logs.query.Query.metadataFromGrpc')
  @patch('microservice.models.logs.query.Parser')
  def testKhaleesiSaveNewEmpty(
      self,
      parser   : MagicMock,
      metadata : MagicMock,
      parent   : MagicMock,
      string   : MagicMock,
      timestamp: MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    # Prepare data.
    string.return_value = 'parsed-string'
    now = datetime.now(tz = timezone.utc)
    timestamp.return_value = now
    instance               = Query()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = GrpcQueryRequest()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parser.assert_called_once()
    metadata.assert_called_once()
    parent.assert_called_once()

  @patch('microservice.models.logs.query.Query.metadataToGrpc')
  def testToGrpc(self, metadata: MagicMock) -> None :
    """Test that general mapping to gRPC works."""
    # Prepare data.
    instance = Query(
      reportedStart = datetime.now(tz = timezone.utc),
      reportedEnd   = datetime.now(tz = timezone.utc),
      raw           = 'raw',
      normalized    = 'normalized',
      tables        = 'table1',
      columns       = 'column1,column2',
    )
    # Execute test.
    result = instance.toGrpc()
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual(
      instance.reportedStart,
      result.query.start.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      instance.reportedEnd,
      result.query.end.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(instance.raw       , result.query.raw)
    self.assertEqual(instance.normalized, result.query.normalized)
    self.assertEqual(1                  , len(result.query.tables))
    self.assertEqual(2                  , len(result.query.columns))
    self.assertEqual(instance.tables    , result.query.tables[0])
    self.assertEqual('column1'          , result.query.columns[0])
    self.assertEqual('column2'          , result.query.columns[1])

  @patch('microservice.models.logs.query.Query.metadataToGrpc')
  def testToGrpcEmpty(self, metadata: MagicMock) -> None :
    """Test that mapping to gRPC for empty queries works."""
    # Prepare data.
    query = Query()
    # Execute test.
    query.toGrpc()
    # Assert result.
    metadata.assert_called_once()

  def _createGrpcQuery(self, *, string: MagicMock, timestamp: MagicMock) -> GrpcQueryRequest :
    """Utility method for creating gRPC Queries."""
    string.return_value = 'parsed-string'
    now = datetime.now(tz = timezone.utc)
    timestamp.return_value = now
    grpc = GrpcQueryRequest()

    grpc.query.start.FromDatetime(datetime.now(tz = timezone.utc))
    grpc.query.end.FromDatetime(datetime.now(tz = timezone.utc))

    grpc.query.raw        = 'raw'
    grpc.query.normalized = 'normalized'
    grpc.query.tables.append('table1')
    grpc.query.columns.append('column1')
    grpc.query.columns.append('column2')

    return grpc
