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
from khaleesi.core.shared.state import STATE, Query
from khaleesi.core.testUtil.exceptions import defaultKhaleesiException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest,
  GrpcResponseRequest,
  Error,
  Event,
  EmptyRequest,
  HttpRequest,
  HttpResponseRequest,
)


class StructuredTestLogger(StructuredLogger):
  """Test class for testing the structured logger."""

  sender = MagicMock()

  def sendLogSystemHttpRequest(self, *, httpRequest: EmptyRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = httpRequest)

  def sendLogHttpRequest(self, *, httpRequest: HttpRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = httpRequest)

  def sendLogHttpResponse(self, *, httpResponse: HttpResponseRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(response = httpResponse)

  def sendLogGrpcRequest(self, *, grpcRequest: GrpcRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = grpcRequest)

  def sendLogGrpcResponse(self, *, grpcResponse: GrpcResponseRequest) -> None :
    """Send the log response to the logging facility."""
    self.sender.send(response = grpcResponse)

  def sendLogError(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    self.sender.send(error = error)

  def sendLogEvent(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    self.sender.send(event = event)


@patch('khaleesi.core.logging.structuredLogger.LOGGER')
class TestStructuredLogger(SimpleTestCase):
  """Test the structured logger."""

  logger = StructuredTestLogger()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogGrpcRequest(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    metadata.reset_mock()
    upstreamRequest = RequestMetadata()
    upstreamRequest.caller.grpcRequestId   = 'request-id'
    upstreamRequest.caller.khaleesiGate    = 'khaleesi-gate'
    upstreamRequest.caller.khaleesiService = 'khaleesi-service'
    upstreamRequest.caller.grpcService     = 'grpc-service'
    upstreamRequest.caller.grpcMethod      = 'grpc-method'
    # Perform test.
    self.logger.logGrpcRequest(upstreamRequest = upstreamRequest)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    self.assertEqual(2, logger.info.call_count)
    metadata.assert_called_once()
    logGrpcRequest = cast(GrpcRequest, self.logger.sender.send.call_args.kwargs['request'])
    self.assertEqual(upstreamRequest.caller, logGrpcRequest.upstreamRequest)

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
  def testLogSystemRequest(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a system request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    metadata.reset_mock()
    httpRequestId = 'http-request'
    grpcRequestId = 'grpc-request'
    grpcMethod    = 'grpc-method'
    # Perform test.
    self.logger.logSystemGrpcRequest(
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
  def testLogSystemHttpRequest(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    httpRequestId = 'http-request'
    # Perform test.
    self.logger.logSystemHttpRequest(
      httpRequestId = httpRequestId,
      grpcMethod    = 'LIFECYCLE',
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogHttpRequest(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.logHttpRequest()
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
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
        # Perform test.
        self.logger.logSystemHttpResponse(
          httpRequestId = 'http-request',
          status        = status,
          grpcMethod    = 'grpc-method',
        )
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        logResponse = cast(
          HttpResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, logResponse.response.status)
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
  def testLogOkSystemHttpResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.logSystemHttpResponse(
      httpRequestId = 'http-request',
      grpcMethod    = 'grpc-method',
      status        = StatusCode.OK,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    logResponse = cast(
      HttpResponseRequest,
      self.logger.sender.send.call_args.kwargs['response'],
    )
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogNotOkHttpResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        # Perform test.
        self.logger.logHttpResponse(status = status)
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        logResponse = cast(
          HttpResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, logResponse.response.status)
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogOkHttpResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.logHttpResponse(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    logResponse = cast(
      HttpResponseRequest,
      self.logger.sender.send.call_args.kwargs['response'],
    )
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
  def testLogNotOkSystemResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        STATE.reset()
        # Perform test.
        self.logger.logSystemGrpcResponse(
          httpRequestId = 'http-request-id',
          grpcRequestId = 'grpc-request-id',
          grpcMethod    = 'grpcMethod',
          status        = status,
        )
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        logResponse = cast(
          GrpcResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, logResponse.response.status)
        self.assertEqual(0, len(logResponse.queries))
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
  def testLogOkSystemResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    STATE.queries = {
        'one' : [ Query(queryId = ids[0], raw = 'raw', start = datetime.now(tz = timezone.utc)) ],
        'two' : [
            Query(queryId = ids[1], raw = 'raw', start = datetime.now(tz = timezone.utc)),
            Query(queryId = ids[2], raw = 'raw', start = datetime.now(tz = timezone.utc)),
        ],
        'zero': [],
    }
    # Perform test.
    self.logger.logSystemGrpcResponse(
      httpRequestId = 'http-request-id',
      grpcRequestId = 'grpc-request-id',
      grpcMethod    = 'grpc-method',
      status        = StatusCode.OK,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    logResponse = cast(GrpcResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    self.assertEqual(3, len(logResponse.queries))
    for queryId in ids:
      self.assertIn(queryId, [ query.id for query in logResponse.queries ])
    connections = [ query.connection for query in logResponse.queries ]
    self.assertIn('one', connections)
    self.assertIn('two', connections)
    self.assertNotIn('three', connections)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogNotOkResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        STATE.reset()
        # Perform test.
        self.logger.logGrpcResponse(status = status)
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        logResponse = cast(
          GrpcResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, logResponse.response.status)
        self.assertEqual(0, len(logResponse.queries))
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addRequestMetadata')
  def testLogOkResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    STATE.queries = {
        'one' : [ Query(queryId = ids[0], raw = 'raw', start = datetime.now(tz = timezone.utc)) ],
        'two' : [
            Query(queryId = ids[1], raw = 'raw', start = datetime.now(tz = timezone.utc)),
            Query(queryId = ids[2], raw = 'raw', start = datetime.now(tz = timezone.utc)),
        ],
        'zero': [],
    }
    # Perform test.
    self.logger.logGrpcResponse(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    logResponse = cast(GrpcResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    self.assertEqual(3, len(logResponse.queries))
    for queryId in ids:
      self.assertIn(queryId, [ query.id for query in logResponse.queries ])
    metadata.assert_called_once()

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
          # Perform test.
          self.logger.logError(exception = exception)
          # Assert result.
          self.logger.sender.send.assert_called_once()
          self.assertEqual(2, logger.log.call_count)
          logError = cast(Error, self.logger.sender.send.call_args.kwargs['error'])
          self.assertIsNotNone(logError.id)
          self.assertEqual(status.name  , logError.status)
          self.assertEqual(loglevel.name, logError.loglevel)
          self._assertError(exception = exception, logError = logError)
          metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
  def testLogSystemError(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging an error."""
    httpRequestId = 'http-request'
    grpcRequestId = 'grpc-request'
    grpcMethod    = 'grpc-method'
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          self.logger.sender.reset_mock()
          logger.reset_mock()
          metadata.reset_mock()
          exception = defaultKhaleesiException(status = status, loglevel = loglevel)
          # Perform test.
          self.logger.logSystemError(
            exception     = exception,
            httpRequestId = httpRequestId,
            grpcRequestId = grpcRequestId,
            grpcMethod    = grpcMethod,
          )
          # Assert result.
          self.logger.sender.send.assert_called_once()
          self.assertEqual(2, logger.log.call_count)
          logError = cast(Error, self.logger.sender.send.call_args.kwargs['error'])
          self.assertIsNotNone(logError.id)
          self.assertEqual(status.name  , logError.status)
          self.assertEqual(loglevel.name, logError.loglevel)
          self._assertError(exception = exception, logError = logError)
          metadata.assert_called_once()

  @patch('khaleesi.core.logging.structuredLogger.addGrpcServerSystemRequestMetadata')
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
          for loggerSendMetric in [True, False]:
            with self.subTest(
                action           = actionLabel,
                result           = resultLabel,
                user             = userLabel,
                loggerSendMetric = loggerSendMetric,
            ):
              # Prepare data.
              requestMetadata.reset_mock()
              self.logger.sender.reset_mock()
              logger.reset_mock()
              owner      = User()
              owner.type = userType
              owner.id   = 'user'
              # Perform test.
              self.logger.logSystemEvent(
                grpcMethod       = method,
                httpRequestId    = httpRequestId,
                grpcRequestId    = grpcRequestId,
                target           = target,
                owner            = owner,
                action           = actionType,
                result           = resultType,
                details          = details,
                loggerSendMetric = loggerSendMetric,
              )
              # Assert result.
              requestMetadata.assert_called_once()
              self.logger.sender.send.assert_called_once()
              self.assertEqual(
                1,
                logger.info.call_count + logger.warning.call_count + logger.error.call_count
                + logger.fatal.call_count,
              )
              logEvent = cast(Event, self.logger.sender.send.call_args.kwargs['event'])
              self.assertIsNotNone(logEvent.id)
              self.assertIsNotNone(logEvent.target.type)
              self.assertEqual(target          , logEvent.target.id)
              self.assertEqual(owner.id        , logEvent.target.owner.id)
              self.assertEqual(owner.type      , logEvent.target.owner.type)
              self.assertEqual(''              , logEvent.action.customType)
              self.assertEqual(actionType      , logEvent.action.crudType)
              self.assertEqual(resultType      , logEvent.action.result)
              self.assertEqual(details         , logEvent.action.details)
              self.assertEqual(loggerSendMetric, logEvent.loggerSendMetric)

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
            owner      = User()
            owner.type = userType
            owner.id   = 'user'
            # Perform test.
            self.logger.logEvent(
              target     = target,
              targetType = targetType,
              owner      = owner,
              action     = action,
              actionCrud = actionType,
              result     = resultType,
              details    = details,
            )
            # Assert result.
            requestMetadata.assert_called_once()
            self.logger.sender.send.assert_called_once()
            self.assertEqual(
              1,
              logger.info.call_count + logger.warning.call_count + logger.error.call_count
              + logger.fatal.call_count,
            )
            logEvent = cast(Event, self.logger.sender.send.call_args.kwargs['event'])
            self.assertIsNotNone(logEvent.id)
            self.assertEqual(target    , logEvent.target.id)
            self.assertEqual(targetType, logEvent.target.type)
            self.assertEqual(owner.id  , logEvent.target.owner.id)
            self.assertEqual(owner.type, logEvent.target.owner.type)
            self.assertEqual(action    , logEvent.action.customType)
            self.assertEqual(actionType, logEvent.action.crudType)
            self.assertEqual(resultType, logEvent.action.result)
            self.assertEqual(details   , logEvent.action.details)
            self.assertEqual(False     , logEvent.loggerSendMetric)

  def _assertError(self, exception: KhaleesiException, logError: Error) -> None :
    self.assertEqual(exception.gate          , logError.gate)
    self.assertEqual(exception.service       , logError.service)
    self.assertEqual(exception.publicKey     , logError.publicKey)
    self.assertEqual(exception.publicDetails , logError.publicDetails)
    self.assertEqual(exception.privateMessage, logError.privateMessage)
    self.assertEqual(exception.privateDetails, logError.privateDetails)
    self.assertEqual(exception.stacktrace    , logError.stacktrace)


class TestStructuredGrpcLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredGrpcLogger()

  def testSendLogSystemHttpRequest(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogSystemHttpRequest = MagicMock()
    # Perform test.
    self.logger.sendLogSystemHttpRequest(httpRequest = MagicMock())
    # Assert result.
    self.logger.stub.LogSystemHttpRequest.assert_called_once()

  def testSendLogHttpRequest(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogHttpRequest = MagicMock()
    # Perform test.
    self.logger.sendLogHttpRequest(httpRequest = MagicMock())
    # Assert result.
    self.logger.stub.LogHttpRequest.assert_called_once()

  def testSendLogHttpResponse(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogHttpRequestResponse = MagicMock()
    # Perform test.
    self.logger.sendLogHttpResponse(httpResponse = MagicMock())
    # Assert result.
    self.logger.stub.LogHttpRequestResponse.assert_called_once()

  def testSendLogGrpcRequest(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogGrpcRequest = MagicMock()
    # Perform test.
    self.logger.sendLogGrpcRequest(grpcRequest = MagicMock())
    # Assert result.
    self.logger.stub.LogGrpcRequest.assert_called_once()

  def testSendLogGrpcResponse(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogGrpcResponse = MagicMock()
    # Perform test.
    self.logger.sendLogGrpcResponse(grpcResponse = MagicMock())
    # Assert result.
    self.logger.stub.LogGrpcResponse.assert_called_once()

  def testSendLogError(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogError = MagicMock()
    # Perform test.
    self.logger.sendLogError(error = MagicMock())
    # Assert result.
    self.logger.stub.LogError.assert_called_once()

  def testSendLogEvent(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogEvent = MagicMock()
    # Perform test.
    self.logger.sendLogEvent(event = MagicMock())
    # Assert result.
    self.logger.stub.LogEvent.assert_called_once()


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
