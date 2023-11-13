"""Test the structured logger."""

# Python.
from datetime import datetime, timezone
from typing import cast
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.structuredLogger import (
  StructuredGrpcLogger,
  StructuredLogger,
  instantiateStructuredLogger,
)
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.exceptions import defaultKhaleesiException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import GrpcCallerDetails, User
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequestRequest,
  ErrorRequest,
  Event, EventRequest,
  HttpRequestRequest,
  ResponseRequest,
  Query,
)


class StructuredTestLogger(StructuredLogger):
  """Test class for testing the structured logger."""

  sender = MagicMock()

  def sendLogHttpRequest(self, *, grpc: HttpRequestRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(grpc = grpc)

  def sendLogHttpResponse(self, *, grpc: ResponseRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(grpc = grpc)

  def sendLogGrpcRequest(self, *, grpc: GrpcRequestRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(grpc = grpc)

  def sendLogGrpcResponse(self, *, grpc: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    self.sender.send(grpc = grpc)

  def sendLogEvent(self, *, grpc: EventRequest) -> None :
    """Send the log event to the logging facility."""
    self.sender.send(grpc = grpc)

  def sendLogError(self, *, grpc: ErrorRequest) -> None :
    """Send the log error to the logging facility."""
    self.sender.send(grpc = grpc)


@patch('khaleesi.core.logging.structuredLogger.LOGGER')
class TestStructuredLogger(SimpleTestCase):
  """Test the structured logger."""

  logger = StructuredTestLogger()

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogHttpRequest(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    httpRequestId = 'http-request'
    # Execute test.
    self.logger.logHttpRequest(httpRequestId = httpRequestId, method = 'LIFECYCLE')
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogNotOkSystemHttpResponse(
      self,
      metadata: MagicMock,
      logger  : MagicMock,
  ) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        # Execute test.
        self.logger.logHttpResponse(
          httpRequestId = 'http-request',
          status        = status,
          method        = 'method',
        )
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        logResponse = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['grpc'])
        self.assertEqual(status.name, logResponse.response.status)
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogOkSystemHttpResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Execute test.
    self.logger.logHttpResponse(
      httpRequestId = 'http-request',
      method        = 'method',
      status        = StatusCode.OK,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    logResponse = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['grpc'])
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogGrpcRequest(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    metadata.reset_mock()
    upstreamRequest = GrpcCallerDetails()
    upstreamRequest.requestId = 'request-id'
    upstreamRequest.site      = 'site'
    upstreamRequest.app       = 'app'
    upstreamRequest.service   = 'service'
    upstreamRequest.method    = 'method'
    # Execute test.
    self.logger.logGrpcRequest(upstreamRequest = upstreamRequest)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    self.assertEqual(2, logger.info.call_count)
    metadata.assert_called_once()
    logGrpcRequest = cast(GrpcRequestRequest, self.logger.sender.send.call_args.kwargs['grpc'])
    self.assertEqual(upstreamRequest, logGrpcRequest.request.upstreamRequest)

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogSystemGrpcRequest(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a system request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    metadata.reset_mock()
    httpRequestId = 'http-request'
    grpcRequestId = 'grpc-request'
    method        = 'method'
    # Execute test.
    self.logger.logSystemGrpcRequest(
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      method        = method,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogNotOkGrpcResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        STATE.reset()
        # Execute test.
        self.logger.logGrpcResponse(status = status)
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        logResponse = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['grpc'])
        self.assertEqual(status.name, logResponse.response.status)
        self.assertEqual(0, len(logResponse.queries))
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogOkGrpcResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    for _ in ids:
      query = Query()
      query.raw = 'raw'
      query.start.FromDatetime(datetime.now(tz = timezone.utc))
      STATE.queries.append(query)
    # Execute test.
    self.logger.logGrpcResponse(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    logResponse = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['grpc'])
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    self.assertEqual(3, len(logResponse.queries))
    for query in logResponse.queries:
      self.assertEqual('raw', query.raw)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogNotOkSystemGrpcResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        STATE.reset()
        # Execute test.
        self.logger.logSystemGrpcResponse(
          httpRequestId = 'http-request-id',
          grpcRequestId = 'grpc-request-id',
          method        = 'method',
          status        = status,
        )
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        logResponse = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['grpc'])
        self.assertEqual(status.name, logResponse.response.status)
        self.assertEqual(0, len(logResponse.queries))
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogOkSystemGrpcResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    for _ in ids:
      query = Query()
      query.raw = 'raw'
      query.start.FromDatetime(datetime.now(tz = timezone.utc))
      STATE.queries.append(query)
    # Execute test.
    self.logger.logSystemGrpcResponse(
      httpRequestId = 'http-request-id',
      grpcRequestId = 'grpc-request-id',
      method        = 'method',
      status        = StatusCode.OK,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    logResponse = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['grpc'])
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    self.assertEqual(3, len(logResponse.queries))
    for query in logResponse.queries:
      self.assertEqual('raw', query.raw)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogEvent(self, requestMetadata: MagicMock, logger: MagicMock) -> None :
    """Test logging an event."""
    details    = 'details'
    target     = 'target'
    targetType = 'target-type'
    action     = 'action'
    for actionLabel, actionType in Event.Action.ActionType.items():
      for resultLabel, resultType in Event.Action.ResultType.items():
        for userLabel, userType in User.UserType.items():
          with self.subTest(action = actionLabel, result = resultLabel, user = userLabel):
            # Prepare data.
            requestMetadata.reset_mock()
            self.logger.sender.reset_mock()
            logger.reset_mock()
            event = Event()
            event.target.id         = target
            event.target.type       = targetType
            event.target.owner.type = userType
            event.target.owner.id   = 'user'
            event.action.crudType   = actionType
            event.action.customType = action
            event.action.result     = resultType
            event.action.details    = details
            # Execute test.
            self.logger.logEvent(event = event)
            # Assert result.
            requestMetadata.assert_called_once()
            self.logger.sender.send.assert_called_once()
            self.assertEqual(
              1,
              logger.info.call_count + logger.warning.call_count + logger.error.call_count
              + logger.fatal.call_count,
            )
            logEvent = cast(EventRequest, self.logger.sender.send.call_args.kwargs['grpc'])
            self.assertEqual(target                 , logEvent.event.target.id)
            self.assertEqual(targetType             , logEvent.event.target.type)
            self.assertEqual(event.target.owner.id  , logEvent.event.target.owner.id)
            self.assertEqual(event.target.owner.type, logEvent.event.target.owner.type)
            self.assertEqual(action                 , logEvent.event.action.customType)
            self.assertEqual(actionType             , logEvent.event.action.crudType)
            self.assertEqual(resultType             , logEvent.event.action.result)
            self.assertEqual(details                , logEvent.event.action.details)

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogSystemEvent(self, requestMetadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a system event."""
    method        = 'LIFECYCLE'
    details       = 'details'
    httpRequestId = 'http-request'
    grpcRequestId = 'grpc-request'
    target        = 'target'
    for actionLabel, actionType in Event.Action.ActionType.items():
      for resultLabel, resultType in Event.Action.ResultType.items():
        for userLabel, userType in User.UserType.items():
          with self.subTest(action = actionLabel, result = resultLabel, user = userLabel):
            # Prepare data.
            requestMetadata.reset_mock()
            self.logger.sender.reset_mock()
            logger.reset_mock()
            event = Event()
            event.target.id         = target
            event.target.owner.type = userType
            event.target.owner.id   = 'user'
            event.action.crudType   = actionType
            event.action.result     = resultType
            event.action.details    = details
            # Execute test.
            self.logger.logSystemEvent(
              method    = method,
              httpRequestId = httpRequestId,
              grpcRequestId = grpcRequestId,
              event         = event,
            )
            # Assert result.
            requestMetadata.assert_called_once()
            self.logger.sender.send.assert_called_once()
            self.assertEqual(
              1,
              logger.info.call_count + logger.warning.call_count + logger.error.call_count
              + logger.fatal.call_count,
            )
            logEvent = cast(EventRequest, self.logger.sender.send.call_args.kwargs['grpc'])
            self.assertIsNotNone(logEvent.event.target.type)
            self.assertEqual(target                 , logEvent.event.target.id)
            self.assertEqual(event.target.owner.id  , logEvent.event.target.owner.id)
            self.assertEqual(event.target.owner.type, logEvent.event.target.owner.type)
            self.assertEqual(''                     , logEvent.event.action.customType)
            self.assertEqual(actionType             , logEvent.event.action.crudType)
            self.assertEqual(resultType             , logEvent.event.action.result)
            self.assertEqual(details                , logEvent.event.action.details)

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogError(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging an error."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          self.logger.sender.reset_mock()
          logger.reset_mock()
          metadata.reset_mock()
          exception = defaultKhaleesiException(status = status, loglevel = loglevel)
          # Execute test.
          self.logger.logError(exception = exception)
          # Assert result.
          self.logger.sender.send.assert_called_once()
          self.assertEqual(2, logger.log.call_count)
          logError = cast(ErrorRequest, self.logger.sender.send.call_args.kwargs['grpc'])
          self.assertEqual(status.name  , logError.error.status)
          self.assertEqual(loglevel.name, logError.error.loglevel)
          self._assertError(exception = exception, logError = logError)
          metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogSystemError(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging an error."""
    httpRequestId = 'http-request'
    grpcRequestId = 'grpc-request'
    method        = 'method'
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          self.logger.sender.reset_mock()
          logger.reset_mock()
          metadata.reset_mock()
          exception = defaultKhaleesiException(status = status, loglevel = loglevel)
          # Execute test.
          self.logger.logSystemError(
            exception     = exception,
            httpRequestId = httpRequestId,
            grpcRequestId = grpcRequestId,
            method        = method,
          )
          # Assert result.
          self.logger.sender.send.assert_called_once()
          self.assertEqual(2, logger.log.call_count)
          logError = cast(ErrorRequest, self.logger.sender.send.call_args.kwargs['grpc'])
          self.assertEqual(status.name  , logError.error.status)
          self.assertEqual(loglevel.name, logError.error.loglevel)
          self._assertError(exception = exception, logError = logError)
          metadata.assert_called_once()

  def _assertError(self, exception: KhaleesiException, logError: ErrorRequest) -> None :
    self.assertEqual(exception.site          , logError.error.site)
    self.assertEqual(exception.app           , logError.error.app)
    self.assertEqual(exception.publicKey     , logError.error.publicKey)
    self.assertEqual(exception.publicDetails , logError.error.publicDetails)
    self.assertEqual(exception.privateMessage, logError.error.privateMessage)
    self.assertEqual(exception.privateDetails, logError.error.privateDetails)
    self.assertEqual(exception.stacktrace    , logError.error.stacktrace)


class TestStructuredGrpcLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredGrpcLogger()

  def testSendLogHttpRequest(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogHttpRequest = MagicMock()
    # Execute test.
    self.logger.sendLogHttpRequest(grpc = MagicMock())
    # Assert result.
    self.logger.stub.LogHttpRequest.assert_called_once()

  def testSendLogHttpResponse(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogHttpRequestResponse = MagicMock()
    # Execute test.
    self.logger.sendLogHttpResponse(grpc = MagicMock())
    # Assert result.
    self.logger.stub.LogHttpRequestResponse.assert_called_once()

  def testSendLogGrpcRequest(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogGrpcRequest = MagicMock()
    # Execute test.
    self.logger.sendLogGrpcRequest(grpc = MagicMock())
    # Assert result.
    self.logger.stub.LogGrpcRequest.assert_called_once()

  def testSendLogGrpcResponse(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogGrpcResponse = MagicMock()
    # Execute test.
    self.logger.sendLogGrpcResponse(grpc = MagicMock())
    # Assert result.
    self.logger.stub.LogGrpcResponse.assert_called_once()

  def testSendLogEvent(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogEvent = MagicMock()
    # Execute test.
    self.logger.sendLogEvent(grpc = MagicMock())
    # Assert result.
    self.logger.stub.LogEvent.assert_called_once()

  def testSendLogError(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogError = MagicMock()
    # Execute test.
    self.logger.sendLogError(grpc = MagicMock())
    # Assert result.
    self.logger.stub.LogError.assert_called_once()


class StructuredLoggerInstantiationTest(SimpleTestCase):
  """Test instantiation."""

  @patch('khaleesi.core.logging.structuredLogger.LOGGER')
  @patch('khaleesi.core.logging.structuredLogger.importSetting')
  def testInstantiation(self, importSetting: MagicMock, *_: MagicMock) -> None :
    """Test instantiation."""
    # Execute test.
    instantiateStructuredLogger()
    # Assert result.
    importSetting.assert_called_once()
