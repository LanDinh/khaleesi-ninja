"""Test the structured logger."""
# Python.
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from microservice.models.logs.query import Query
from microservice.structuredLogger import StructuredDbLogger


@patch('microservice.structuredLogger.LOGGER')
class TestStructuredDbLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredDbLogger()

  @patch('microservice.structuredLogger.DbHttpRequest')
  def testSendLogHttpRequest(self, dbHttpRequest: MagicMock, *_: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    request = MagicMock()
    # Perform test.
    self.logger.sendLogHttpRequest(grpc = request)
    # Assert result.
    dbHttpRequest.return_value.khaleesiSave.assert_called_once()

  @patch('microservice.structuredLogger.DbHttpRequest')
  def testSendLogHttpResponse(self, dbHttpRequest: MagicMock, *_: MagicMock) -> None :
    """Test sending a log response."""
    # Prepare data.
    response = MagicMock()
    # Perform test.
    self.logger.sendLogHttpResponse(grpc = response)
    # Assert result.
    dbHttpRequest.objects.get.return_value.finish.assert_called_once()

  @patch('microservice.structuredLogger.SERVICE_REGISTRY')
  @patch('microservice.structuredLogger.DbGrpcRequest')
  def testSendLogGrpcRequest(
      self,
      dbGrpcRequest  : MagicMock,
      serviceRegistry: MagicMock,
      *_             : MagicMock,
  ) -> None :
    """Test sending a log request."""
    # Prepare data.
    grpcRequest = MagicMock()
    # Perform test.
    self.logger.sendLogGrpcRequest(grpc = grpcRequest)
    # Assert result.
    dbGrpcRequest.return_value.khaleesiSave.assert_called_once_with(grpc = grpcRequest)
    serviceRegistry.addCall.assert_called_once()

  @patch('microservice.structuredLogger.DbQuery')
  @patch('microservice.structuredLogger.DbGrpcRequest')
  @patch('microservice.structuredLogger.DbHttpRequest')
  def testSendLogGrpcResponse(
      self,
      dbHttpRequest: MagicMock,
      dbGrpcRequest: MagicMock,
      dbQuery      : MagicMock,
      *_           : MagicMock,
  ) -> None :
    """Test sending a log response."""
    # Prepare data.
    response = MagicMock()
    now = datetime.now().replace(tzinfo = timezone.utc)
    dbQuery.objects.logQueries.return_value = [ Query() ]
    dbQuery.objects.logQueries.return_value[0].reportedStart = now
    dbQuery.objects.logQueries.return_value[0].reportedEnd   = now + timedelta(days = 1)
    # Perform test.
    self.logger.sendLogGrpcResponse(grpc = response)
    # Assert result.
    dbHttpRequest.objects.get.return_value.addChildDuration.assert_called_once()
    dbGrpcRequest.objects.get.return_value.finish.assert_called_once()
    dbGrpcRequest.objects.get.return_value.khaleesiSave.assert_called_once()
    dbQuery.objects.logQueries.assert_called_once()

  @patch('microservice.structuredLogger.DbEvent')
  def testSendLogEvent(self, dbEvent: MagicMock, *_: MagicMock) -> None :
    """Test sending a log event."""
    # Prepare data.
    event = MagicMock()
    # Perform test.
    self.logger.sendLogEvent(grpc = event)
    # Assert result.
    dbEvent.return_value.khaleesiSave.assert_called_once()

  @patch('microservice.structuredLogger.DbError')
  def testSendLogError(self, dbError: MagicMock, *_: MagicMock) -> None :
    """Test sending a log error."""
    # Prepare data.
    error = MagicMock()
    # Perform test.
    self.logger.sendLogError(grpc = error)
    # Assert result.
    dbError.return_value.khaleesiSave.assert_called_once()
