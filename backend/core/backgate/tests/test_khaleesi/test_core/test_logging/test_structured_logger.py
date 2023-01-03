"""Test the structured logger."""

# Python.
from typing import cast
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.structured_logger import StructuredGrpcLogger, StructuredLogger
from khaleesi.core.logging.text_logger import LogLevel
from khaleesi.core.shared.state import STATE, Query
from khaleesi.core.test_util.exceptions import default_khaleesi_exception
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import (
  Request,
  ResponseRequest,
  Error,
  Event,
  EmptyRequest,
  BackgateRequest,
  BackgateResponseRequest,
)


class StructuredTestLogger(StructuredLogger):
  """Test class for testing the structured logger."""

  sender = MagicMock()

  def send_log_system_backgate_request(self, *, backgate_request: EmptyRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = backgate_request)

  def send_log_backgate_request(self, *, backgate_request: BackgateRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = backgate_request)

  def send_log_backgate_response(self, *, response: BackgateResponseRequest) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(response = response)

  def send_log_request(self, *, request: Request) -> None :
    """Send the log request to the logging facility."""
    self.sender.send(request = request)

  def send_log_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    self.sender.send(response = response)

  def send_log_error(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    self.sender.send(error = error)

  def send_log_event(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    self.sender.send(event = event)


@patch('khaleesi.core.logging.structured_logger.LOGGER')
class TestStructuredLogger(SimpleTestCase):
  """Test the structured logger."""

  logger = StructuredTestLogger(channel_manager = MagicMock())

  def test_log_request(self, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    upstream_request = RequestMetadata()
    upstream_request.caller.request_id       = 'request-id'
    upstream_request.caller.khaleesi_gate    = 'khaleesi-gate'
    upstream_request.caller.khaleesi_service = 'khaleesi-service'
    upstream_request.caller.grpc_service     = 'grpc-service'
    upstream_request.caller.grpc_method      = 'grpc-method'
    # Perform test.
    self.logger.log_request(upstream_request = upstream_request)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    self.assertEqual(2, logger.info.call_count)
    log_request = cast(Request, self.logger.sender.send.call_args.kwargs['request'])
    self.assertEqual(upstream_request.caller, log_request.upstream_request)

  def test_log_system_backgate_request(self, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    backgate_request_id = 'backgate-request'
    # Perform test.
    self.logger.log_system_backgate_request(
      backgate_request_id = backgate_request_id,
      grpc_method = 'LIFECYCLE',
    )
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    log_request = cast(EmptyRequest, self.logger.sender.send.call_args.kwargs['request'])
    self.assertEqual(backgate_request_id, log_request.request_metadata.caller.backgate_request_id)

  def test_log_backgate_request(self, logger: MagicMock) -> None :
    """Test logging a request."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.log_backgate_request()
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    cast(EmptyRequest, self.logger.sender.send.call_args.kwargs['request'])

  def test_log_not_ok_backgate_response(self, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        # Perform test.
        self.logger.log_backgate_response(status = status)
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        log_response = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
        self.assertEqual(status.name, log_response.response.status)

  def test_log_ok_backgate_response(self, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    # Perform test.
    self.logger.log_backgate_response(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called_once()
    log_response = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
    self.assertEqual(StatusCode.OK.name, log_response.response.status)

  def test_log_not_ok_response(self, logger: MagicMock) -> None :
    """Test logging a response."""
    for status in [s for s in StatusCode if s != StatusCode.OK]:
      with self.subTest(status = status.name):
        # Prepare data.
        self.logger.sender.reset_mock()
        logger.reset_mock()
        STATE.reset()
        # Perform test.
        self.logger.log_response(status = status)
        # Assert result.
        self.logger.sender.send.assert_called_once()
        logger.warning.assert_called_once()
        log_response = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
        self.assertEqual(status.name, log_response.response.status)
        self.assertEqual(0, len(log_response.queries))

  def test_log_ok_response(self, logger: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    self.logger.sender.reset_mock()
    logger.reset_mock()
    ids = [ 'id0', 'id1', 'id2', ]
    STATE.reset()
    STATE.queries = {
        'one' : [ Query(query_id = ids[0], raw = 'raw') ],
        'two' : [ Query(query_id = ids[1], raw = 'raw'), Query(query_id = ids[2], raw = 'raw') ],
        'zero': [],
    }
    # Perform test.
    self.logger.log_response(status = StatusCode.OK)
    # Assert result.
    self.logger.sender.send.assert_called_once()
    logger.info.assert_called()
    log_response = cast(ResponseRequest, self.logger.sender.send.call_args.kwargs['response'])
    self.assertEqual(StatusCode.OK.name, log_response.response.status)
    self.assertEqual(3, len(log_response.queries))
    for query_id in ids:
      self.assertIn(query_id, [ query.id for query in log_response.queries ])

  def test_log_error(self, logger: MagicMock) -> None :
    """Test logging an error."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          self.logger.sender.reset_mock()
          logger.reset_mock()
          exception = default_khaleesi_exception(status = status, loglevel = loglevel)
          # Perform test.
          self.logger.log_error(exception = exception)
          # Assert result.
          self.logger.sender.send.assert_called_once()
          self.assertEqual(2, logger.log.call_count)
          log_error = cast(Error, self.logger.sender.send.call_args.kwargs['error'])
          self.assertEqual(status.name              , log_error.status)
          self.assertEqual(loglevel.name            , log_error.loglevel)
          self.assertEqual(exception.gate           , log_error.gate)
          self.assertEqual(exception.service        , log_error.service)
          self.assertEqual(exception.public_key     , log_error.public_key)
          self.assertEqual(exception.public_details , log_error.public_details)
          self.assertEqual(exception.private_message, log_error.private_message)
          self.assertEqual(exception.private_details, log_error.private_details)
          self.assertEqual(exception.stacktrace     , log_error.stacktrace)

  def test_log_system_event(self, logger: MagicMock) -> None :
    """Test logging an event."""
    method              = 'LIFECYCLE'
    details             = 'details'
    backgate_request_id = 'backgate-request'
    for action_label, action_type in Event.Action.ActionType.items():
      for result_label, result_type in Event.Action.ResultType.items():
        for user_label, user_type in User.UserType.items():
          for logger_send_metric in [True, False]:
            with self.subTest(
                action = action_label,
                result = result_label,
                user = user_label,
                logger_send_metric = logger_send_metric,
            ):
              # Prepare data.
              self.logger.sender.reset_mock()
              logger.reset_mock()
              owner      = User()
              owner.type = user_type
              owner.id   = 'user'
              target = 'target'
              # Perform test.
              self.logger.log_system_event(
                grpc_method         = method,
                backgate_request_id = backgate_request_id,
                target              = target,
                owner               = owner,
                action              = action_type,
                result              = result_type,
                details             = details,
                logger_send_metric  = logger_send_metric,
              )
              # Assert result.
              self.logger.sender.send.assert_called_once()
              self.assertEqual(
                1,
                logger.info.call_count + logger.warning.call_count + logger.error.call_count
                + logger.fatal.call_count,
              )
              log_event = cast(Event, self.logger.sender.send.call_args.kwargs['event'])
              self.assertEqual(
                backgate_request_id,
                log_event.request_metadata.caller.backgate_request_id,
              )
              self.assertEqual(target            , log_event.target.id)
              self.assertEqual(target            , log_event.target.id)
              self.assertEqual(owner.id          , log_event.target.owner.id)
              self.assertEqual(owner.type        , log_event.target.owner.type)
              self.assertEqual(action_type       , log_event.action.crud_type)
              self.assertEqual(result_type       , log_event.action.result)
              self.assertEqual(details           , log_event.action.details)
              self.assertEqual(logger_send_metric, log_event.logger_send_metric)


class TestStructuredGrpcLogger(SimpleTestCase):
  """Test the structured gRPC logger."""

  logger = StructuredGrpcLogger(channel_manager = MagicMock())

  def test_send_log_system_backgate_request(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogSystemBackgateRequest = MagicMock()
    # Perform test.
    self.logger.send_log_system_backgate_request(backgate_request = MagicMock())
    # Assert result.
    self.logger.stub.LogSystemBackgateRequest.assert_called_once()

  def test_send_log_backgate_request(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogBackgateRequest = MagicMock()
    # Perform test.
    self.logger.send_log_backgate_request(backgate_request = MagicMock())
    # Assert result.
    self.logger.stub.LogBackgateRequest.assert_called_once()

  def test_send_log_backgate_response(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogBackgateRequestResponse = MagicMock()
    # Perform test.
    self.logger.send_log_backgate_response(response = MagicMock())
    # Assert result.
    self.logger.stub.LogBackgateRequestResponse.assert_called_once()

  def test_send_log_request(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogRequest = MagicMock()
    # Perform test.
    self.logger.send_log_request(request = MagicMock())
    # Assert result.
    self.logger.stub.LogRequest.assert_called_once()

  def test_send_log_response(self) -> None :
    """Test sending a log request."""
    # Prepare data.
    self.logger.stub.LogResponse = MagicMock()
    # Perform test.
    self.logger.send_log_response(response = MagicMock())
    # Assert result.
    self.logger.stub.LogResponse.assert_called_once()

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
