"""Test the structured logger."""

# Python.
from datetime import datetime, timezone
from typing import cast
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.structured_logger import (
  StructuredGrpcLogger,
  StructuredLogger,
  instantiate_structured_logger,
)
from khaleesi.core.logging.text_logger import LogLevel
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.shared.state import STATE, Query
from khaleesi.core.test_util.exceptions import default_khaleesi_exception
from khaleesi.core.test_util.test_case import SimpleTestCase
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

  def send_log_system_http_request(self, *, http_request: EmptyRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = http_request)

  def send_log_http_request(self, *, http_request: HttpRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = http_request)

  def send_log_http_response(self, *, http_response: HttpResponseRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(response = http_response)

  def send_log_grpc_request(self, *, grpc_request: GrpcRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = grpc_request)

  def send_log_grpc_response(self, *, grpc_response: GrpcResponseRequest) -> None :
    """Send the log response to the logging facility."""
    self.sender.send(response = grpc_response)

  def send_log_error(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    self.sender.send(error = error)

  def send_log_event(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    self.sender.send(event = event)


@patch('khaleesi.core.logging.structured_logger.LOGGER')
class TestStructuredLogger(SimpleTestCase):
  """Test the structured logger."""

  logger = StructuredTestLogger()

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_grpc_request(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    metadata.reset_mock()
    upstream_request = RequestMetadata()
    upstream_request.caller.grpcRequestId   = 'request-id'
    upstream_request.caller.khaleesiGate    = 'khaleesi-gate'
    upstream_request.caller.khaleesiService = 'khaleesi-service'
    upstream_request.caller.grpcService     = 'grpc-service'
    upstream_request.caller.grpcMethod      = 'grpc-method'
    # Perform test.
    self.logger.log_grpc_request(upstream_request = upstream_request)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    self.assertEqual(2, logger.info.call_count)
    metadata.assert_called_once()
    log_grpc_request = cast(GrpcRequest, self.logger.sender.send.call_args.kwargs['request'])
    self.assertEqual(upstream_request.caller, log_grpc_request.upstreamRequest)

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_system_request(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a system request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    metadata.reset_mock()
    http_request_id = 'http-request'
    grpc_request_id = 'grpc-request'
    grpc_method     = 'grpc-method'
    # Perform test.
    self.logger.log_system_grpc_request(
      http_request_id = http_request_id,
      grpc_request_id = grpc_request_id,
      grpc_method         = grpc_method,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_system_http_request(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    http_request_id = 'http-request'
    # Perform test.
    self.logger.log_system_http_request(
      http_request_id = http_request_id,
      grpc_method     = 'LIFECYCLE',
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_http_request(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.log_http_request()
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_not_ok_system_http_response(
      self,
      metadata: MagicMock,
      logger: MagicMock,
  ) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        # Perform test.
        self.logger.log_system_http_response(
          http_request_id = 'http-request',
          status          = status,
          grpc_method     = 'grpc-method',
        )
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        log_response = cast(
          HttpResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, log_response.response.status)
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_ok_system_http_response(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.log_system_http_response(
      http_request_id = 'http-request',
      grpc_method     = 'grpc-method',
      status          = StatusCode.OK,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    log_response = cast(
      HttpResponseRequest,
      self.logger.sender.send.call_args.kwargs['response'],
    )
    self.assertEqual(StatusCode.OK.name, log_response.response.status)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_not_ok_http_response(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        # Perform test.
        self.logger.log_http_response(status = status)
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        log_response = cast(
          HttpResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, log_response.response.status)
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_ok_http_response(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.log_http_response(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    log_response = cast(
      HttpResponseRequest,
      self.logger.sender.send.call_args.kwargs['response'],
    )
    self.assertEqual(StatusCode.OK.name, log_response.response.status)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_not_ok_system_response(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        STATE.reset()
        # Perform test.
        self.logger.log_system_grpc_response(
          http_request_id = 'http-request-id',
          grpc_request_id = 'grpc-request-id',
          grpc_method     = 'grpc_method',
          status          = status,
        )
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        log_response = cast(
          GrpcResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, log_response.response.status)
        self.assertEqual(0, len(log_response.queries))
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_ok_system_response(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    STATE.queries = {
        'one' : [ Query(query_id = ids[0], raw = 'raw', start = datetime.now(tz = timezone.utc)) ],
        'two' : [
            Query(query_id = ids[1], raw = 'raw', start = datetime.now(tz = timezone.utc)),
            Query(query_id = ids[2], raw = 'raw', start = datetime.now(tz = timezone.utc)),
        ],
        'zero': [],
    }
    # Perform test.
    self.logger.log_system_grpc_response(
      http_request_id = 'http-request-id',
      grpc_request_id = 'grpc-request-id',
      grpc_method     = 'grpc-method',
      status          = StatusCode.OK,
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    log_response = cast(GrpcResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
    self.assertEqual(StatusCode.OK.name, log_response.response.status)
    self.assertEqual(3, len(log_response.queries))
    for query_id in ids:
      self.assertIn(query_id, [ query.id for query in log_response.queries ])
    connections = [ query.connection for query in log_response.queries ]
    self.assertIn('one', connections)
    self.assertIn('two', connections)
    self.assertNotIn('three', connections)
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_not_ok_response(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        metadata.reset_mock()
        STATE.reset()
        # Perform test.
        self.logger.log_grpc_response(status = status)
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        log_response = cast(
          GrpcResponseRequest,
          self.logger.sender.send.call_args.kwargs['response'],
        )
        self.assertEqual(status.name, log_response.response.status)
        self.assertEqual(0, len(log_response.queries))
        metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_ok_response(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    STATE.queries = {
        'one' : [ Query(query_id = ids[0], raw = 'raw', start = datetime.now(tz = timezone.utc)) ],
        'two' : [
            Query(query_id = ids[1], raw = 'raw', start = datetime.now(tz = timezone.utc)),
            Query(query_id = ids[2], raw = 'raw', start = datetime.now(tz = timezone.utc)),
        ],
        'zero': [],
    }
    # Perform test.
    self.logger.log_grpc_response(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    log_response = cast(GrpcResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
    self.assertEqual(StatusCode.OK.name, log_response.response.status)
    self.assertEqual(3, len(log_response.queries))
    for query_id in ids:
      self.assertIn(query_id, [ query.id for query in log_response.queries ])
    metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_error(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging an error."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          self.logger.sender.reset_mock()
          logger.reset_mock()
          metadata.reset_mock()
          exception = default_khaleesi_exception(status = status, loglevel = loglevel)
          # Perform test.
          self.logger.log_error(exception = exception)
          # Assert result.
          self.logger.sender.send.assert_called_once()
          self.assertEqual(2, logger.log.call_count)
          log_error = cast(Error, self.logger.sender.send.call_args.kwargs['error'])
          self.assertIsNotNone(log_error.id)
          self.assertEqual(status.name  , log_error.status)
          self.assertEqual(loglevel.name, log_error.loglevel)
          self._assert_error(exception = exception, log_error = log_error)
          metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_system_error(self, metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging an error."""
    http_request_id = 'http-request'
    grpc_request_id = 'grpc-request'
    grpc_method     = 'grpc-method'
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          self.logger.sender.reset_mock()
          logger.reset_mock()
          metadata.reset_mock()
          exception = default_khaleesi_exception(status = status, loglevel = loglevel)
          # Perform test.
          self.logger.log_system_error(
            exception = exception,
            http_request_id = http_request_id,
            grpc_request_id = grpc_request_id,
            grpc_method     = grpc_method,
          )
          # Assert result.
          self.logger.sender.send.assert_called_once()
          self.assertEqual(2, logger.log.call_count)
          log_error = cast(Error, self.logger.sender.send.call_args.kwargs['error'])
          self.assertIsNotNone(log_error.id)
          self.assertEqual(status.name  , log_error.status)
          self.assertEqual(loglevel.name, log_error.loglevel)
          self._assert_error(exception = exception, log_error = log_error)
          metadata.assert_called_once()

  @patch('khaleesi.core.logging.structured_logger.add_grpc_server_system_request_metadata')
  def test_log_system_event(self, request_metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging a system event."""
    method          = 'LIFECYCLE'
    details         = 'details'
    http_request_id = 'http-request'
    grpc_request_id = 'grpc-request'
    target          = 'target'
    for action_label, action_type in Event.Action.ActionType.items():
      for result_label, result_type in Event.Action.ResultType.items():
        for user_label, user_type in User.UserType.items():
          for logger_send_metric in [True, False]:
            with self.subTest(
                action             = action_label,
                result             = result_label,
                user               = user_label,
                logger_send_metric = logger_send_metric,
            ):
              # Prepare data.
              request_metadata.reset_mock()
              self.logger.sender.reset_mock()
              logger.reset_mock()
              owner      = User()
              owner.type = user_type
              owner.id   = 'user'
              # Perform test.
              self.logger.log_system_event(
                grpc_method        = method,
                http_request_id    = http_request_id,
                grpc_request_id    = grpc_request_id,
                target             = target,
                owner              = owner,
                action             = action_type,
                result             = result_type,
                details            = details,
                logger_send_metric = logger_send_metric,
              )
              # Assert result.
              request_metadata.assert_called_once()
              self.logger.sender.send.assert_called_once()
              self.assertEqual(
                1,
                logger.info.call_count + logger.warning.call_count + logger.error.call_count
                + logger.fatal.call_count,
              )
              log_event = cast(Event, self.logger.sender.send.call_args.kwargs['event'])
              self.assertIsNotNone(log_event.id)
              self.assertIsNotNone(log_event.target.type)
              self.assertEqual(target            , log_event.target.id)
              self.assertEqual(owner.id          , log_event.target.owner.id)
              self.assertEqual(owner.type        , log_event.target.owner.type)
              self.assertEqual(''                , log_event.action.customType)
              self.assertEqual(action_type       , log_event.action.crudType)
              self.assertEqual(result_type       , log_event.action.result)
              self.assertEqual(details           , log_event.action.details)
              self.assertEqual(logger_send_metric, log_event.loggerSendMetric)

  @patch('khaleesi.core.logging.structured_logger.add_request_metadata')
  def test_log_event(self, request_metadata: MagicMock, logger: MagicMock) -> None :
    """Test logging an event."""
    details     = 'details'
    target      = 'target'
    target_type = 'target-type'
    action      = 'action'
    for action_label, action_type in Event.Action.ActionType.items():
      for result_label, result_type in Event.Action.ResultType.items():
        for user_label, user_type in User.UserType.items():
          with self.subTest(action = action_label, result = result_label, user = user_label):
            # Prepare data.
            request_metadata.reset_mock()
            self.logger.sender.reset_mock()
            logger.reset_mock()
            owner      = User()
            owner.type = user_type
            owner.id   = 'user'
            # Perform test.
            self.logger.log_event(
              target      = target,
              target_type = target_type,
              owner       = owner,
              action      = action,
              action_crud = action_type,
              result      = result_type,
              details     = details,
            )
            # Assert result.
            request_metadata.assert_called_once()
            self.logger.sender.send.assert_called_once()
            self.assertEqual(
              1,
              logger.info.call_count + logger.warning.call_count + logger.error.call_count
              + logger.fatal.call_count,
            )
            log_event = cast(Event, self.logger.sender.send.call_args.kwargs['event'])
            self.assertIsNotNone(log_event.id)
            self.assertEqual(target     , log_event.target.id)
            self.assertEqual(target_type, log_event.target.type)
            self.assertEqual(owner.id   , log_event.target.owner.id)
            self.assertEqual(owner.type , log_event.target.owner.type)
            self.assertEqual(action     , log_event.action.customType)
            self.assertEqual(action_type, log_event.action.crudType)
            self.assertEqual(result_type, log_event.action.result)
            self.assertEqual(details    , log_event.action.details)
            self.assertEqual(False      , log_event.loggerSendMetric)

  def _assert_error(self, exception: KhaleesiException, log_error: Error) -> None :
    self.assertEqual(exception.gate           , log_error.gate)
    self.assertEqual(exception.service        , log_error.service)
    self.assertEqual(exception.public_key     , log_error.publicKey)
    self.assertEqual(exception.public_details , log_error.publicDetails)
    self.assertEqual(exception.private_message, log_error.privateMessage)
    self.assertEqual(exception.private_details, log_error.privateDetails)
    self.assertEqual(exception.stacktrace     , log_error.stacktrace)


class TestStructuredGrpcLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredGrpcLogger()

  def test_send_log_system_http_request(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogSystemHttpRequest = MagicMock()
    # Perform test.
    self.logger.send_log_system_http_request(http_request = MagicMock())
    # Assert result.
    self.logger.stub.LogSystemHttpRequest.assert_called_once()

  def test_send_log_http_request(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogHttpRequest = MagicMock()
    # Perform test.
    self.logger.send_log_http_request(http_request = MagicMock())
    # Assert result.
    self.logger.stub.LogHttpRequest.assert_called_once()

  def test_send_log_http_response(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogHttpRequestResponse = MagicMock()
    # Perform test.
    self.logger.send_log_http_response(http_response = MagicMock())
    # Assert result.
    self.logger.stub.LogHttpRequestResponse.assert_called_once()

  def test_send_log_grpc_request(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogGrpcRequest = MagicMock()
    # Perform test.
    self.logger.send_log_grpc_request(grpc_request = MagicMock())
    # Assert result.
    self.logger.stub.LogGrpcRequest.assert_called_once()

  def test_send_log_grpc_response(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogGrpcResponse = MagicMock()
    # Perform test.
    self.logger.send_log_grpc_response(grpc_response = MagicMock())
    # Assert result.
    self.logger.stub.LogGrpcResponse.assert_called_once()

  def test_send_log_error(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogError = MagicMock()
    # Perform test.
    self.logger.send_log_error(error = MagicMock())
    # Assert result.
    self.logger.stub.LogError.assert_called_once()

  def test_send_log_event(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogEvent = MagicMock()
    # Perform test.
    self.logger.send_log_event(event = MagicMock())
    # Assert result.
    self.logger.stub.LogEvent.assert_called_once()


class StructuredLoggerInstantiationTest(SimpleTestCase):
  """Test instantiation."""

  @patch('khaleesi.core.logging.structured_logger.LOGGER')
  @patch('khaleesi.core.logging.structured_logger.import_setting')
  def test_instantiation(self, import_setting: MagicMock, *_: MagicMock) -> None :
    """Test instantiation."""
    # Execute test.
    instantiate_structured_logger()
    # Assert result.
    import_setting.assert_called_once()
