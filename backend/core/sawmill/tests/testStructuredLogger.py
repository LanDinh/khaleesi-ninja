"""Test the structured logger."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from microservice.structuredLogger import StructuredDbLogger


class TestStructuredDbLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredDbLogger()

  @patch('microservice.structuredLogger.DbHttpRequest')
  def testSendLogSystemHttpRequest(self, dbHttpRequest: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    request = MagicMock()
    # Perform test.
    self.logger.sendLogSystemHttpRequest(httpRequest = request)
    # Assert result.
    dbHttpRequest.objects.logSystemRequest.assert_called_once_with(grpcRequest = request)

  @patch('microservice.structuredLogger.DbHttpRequest')
  def testSendLogHttpRequest(self, dbHttpRequest: MagicMock) -> None :
    """Test sending a log request."""
    # Prepare data.
    request = MagicMock()
    # Perform test.
    self.logger.sendLogHttpRequest(httpRequest = request)
    # Assert result.
    dbHttpRequest.objects.logRequest.assert_called_once_with(grpcRequest = request)

  @patch('microservice.structuredLogger.DbHttpRequest')
  def testSendLogHttpResponse(self, dbHttpRequest: MagicMock) -> None :
    """Test sending a log response."""
    # Prepare data.
    response = MagicMock()
    # Perform test.
    self.logger.sendLogHttpResponse(httpResponse = response)
    # Assert result.
    dbHttpRequest.objects.logResponse.assert_called_once_with(grpcResponse = response)

  @patch('microservice.structuredLogger.SERVICE_REGISTRY')
  @patch('microservice.structuredLogger.DbGrpcRequest')
  def testSendLogGrpcRequest(
      self,
      dbGrpcRequest : MagicMock,
      serviceRegistry: MagicMock,
  ) -> None :
    """Test sending a log request."""
    # Prepare data.
    grpcRequest = MagicMock()
    # Perform test.
    self.logger.sendLogGrpcRequest(grpcRequest = grpcRequest)
    # Assert result.
    dbGrpcRequest.objects.logRequest.assert_called_once_with(grpcRequest = grpcRequest)
    serviceRegistry.addCall.assert_called_once()

  @patch('microservice.structuredLogger.DbQuery')
  @patch('microservice.structuredLogger.DbGrpcRequest')
  @patch('microservice.structuredLogger.DbHttpRequest')
  def testSendLogGrpcResponse(
      self,
      dbHttpRequest: MagicMock,
      dbGrpcRequest: MagicMock,
      dbQuery      : MagicMock,
  ) -> None :
    """Test sending a log response."""
    # Prepare data.
    response = MagicMock()
    # Perform test.
    self.logger.sendLogGrpcResponse(grpcResponse = response)
    # Assert result.
    dbHttpRequest.objects.addChildDuration.assert_called_once()
    dbGrpcRequest.objects.logResponse.assert_called_once_with(grpcResponse = response)
    dbGrpcRequest.objects.logResponse.return_value.save.assert_called_once_with()
    dbQuery.objects.logQueries.assert_called_once()

  @patch('microservice.structuredLogger.DbError')
  def testSendLogError(self, dbError: MagicMock) -> None :
    """Test sending a log error."""
    # Prepare data.
    error = MagicMock()
    # Perform test.
    self.logger.sendLogError(error = error)
    # Assert result.
    dbError.objects.logError.assert_called_once_with(grpcError = error)

  @patch('microservice.structuredLogger.DbEvent')
  def testSendLogEvent(self, dbEvent: MagicMock) -> None :
    """Test sending a log event."""
    # Prepare data.
    event = MagicMock()
    # Perform test.
    self.logger.sendLogEvent(event = event)
    # Assert result.
    dbEvent.objects.logEvent.assert_called_once_with(grpcEvent = event)
