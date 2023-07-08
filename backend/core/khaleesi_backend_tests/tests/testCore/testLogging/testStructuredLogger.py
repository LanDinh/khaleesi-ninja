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
from khaleesi.proto.core_pb2 import RequestMetadata, User, EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest,
  GrpcResponseRequest,
  Error,
  Event, EventRequest,
  HttpRequest,
  HttpResponseRequest,
  Query,
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

  def sendLogEvent(self, *, event: EventRequest) -> None :
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
    upstreamRequest.grpcCaller.requestId       = 'request-id'
    upstreamRequest.grpcCaller.khaleesiGate    = 'khaleesi-gate'
    upstreamRequest.grpcCaller.khaleesiService = 'khaleesi-service'
    upstreamRequest.grpcCaller.grpcService     = 'grpc-service'
    upstreamRequest.grpcCaller.grpcMethod      = 'grpc-method'
    # Perform test.
    self.logger.logGrpcRequest(upstreamRequest = upstreamRequest)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    self.assertEqual(2, logger.info.call_count)
    metadata.assert_called_once()
    logGrpcRequest = cast(GrpcRequest, self.logger.sender.send.call_args.kwargs['request'])
    self.assertEqual(upstreamRequest.grpcCaller, logGrpcRequest.upstreamRequest)

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
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

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
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

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
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

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
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

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
  def testLogOkSystemResponse(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    for queryId in ids:
      query = Query()
      query.id = queryId
      query.raw = 'raw'
      query.start.FromDatetime(datetime.now(tz = timezone.utc))
      query.connection = 'connection'
      STATE.queries.append(query)
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
    for query in logResponse.queries:
      self.assertIn(query.id, ids)
      self.assertEqual('connection', query.connection)
      self.assertEqual('raw'       , query.raw)
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
    for queryId in ids:
      query = Query()
      query.id = queryId
      query.raw = 'raw'
      query.start.FromDatetime(datetime.now(tz = timezone.utc))
      query.connection = 'connection'
      STATE.queries.append(query)
    # Perform test.
    self.logger.logGrpcResponse(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    logResponse = cast(GrpcResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
    self.assertEqual(StatusCode.OK.name, logResponse.response.status)
    self.assertEqual(3, len(logResponse.queries))
    for query in logResponse.queries:
      self.assertIn(query.id, ids)
      self.assertEqual('connection', query.connection)
      self.assertEqual('raw'       , query.raw)
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

  @patch('khaleesi.core.logging.structuredLogger.addSystemRequestMetadata')
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
            # Perform test.
            self.logger.logSystemEvent(
              grpcMethod    = method,
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
            logEvent = cast(EventRequest, self.logger.sender.send.call_args.kwargs['event'])
            self.assertIsNotNone(logEvent.event.target.type)
            self.assertEqual(target                 , logEvent.event.target.id)
            self.assertEqual(event.target.owner.id  , logEvent.event.target.owner.id)
            self.assertEqual(event.target.owner.type, logEvent.event.target.owner.type)
            self.assertEqual(''                     , logEvent.event.action.customType)
            self.assertEqual(actionType             , logEvent.event.action.crudType)
            self.assertEqual(resultType             , logEvent.event.action.result)
            self.assertEqual(details                , logEvent.event.action.details)

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
            # Perform test.
            self.logger.logEvent(event = event)
            # Assert result.
            requestMetadata.assert_called_once()
            self.logger.sender.send.assert_called_once()
            self.assertEqual(
              1,
              logger.info.call_count + logger.warning.call_count + logger.error.call_count
              + logger.fatal.call_count,
            )
            logEvent = cast(EventRequest, self.logger.sender.send.call_args.kwargs['event'])
            self.assertEqual(target                 , logEvent.event.target.id)
            self.assertEqual(targetType             , logEvent.event.target.type)
            self.assertEqual(event.target.owner.id  , logEvent.event.target.owner.id)
            self.assertEqual(event.target.owner.type, logEvent.event.target.owner.type)
            self.assertEqual(action                 , logEvent.event.action.customType)
            self.assertEqual(actionType             , logEvent.event.action.crudType)
            self.assertEqual(resultType             , logEvent.event.action.result)
            self.assertEqual(details                , logEvent.event.action.details)

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
