"""Test the gRPC server."""

# Python.
import threading
from typing import cast
from unittest.mock import patch, MagicMock

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import TimeoutException, KhaleesiException
from khaleesi.core.testUtil.exceptions import defaultKhaleesiException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event


khaleesiNinjaSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA

@patch('khaleesi.core.grpc.server.reflection')
@patch('khaleesi.core.grpc.server.registerService')
@patch('khaleesi.core.grpc.server.instantiateLoggingInterceptor')
@patch('khaleesi.core.grpc.server.instantiatePrometheusInterceptor')
@patch('khaleesi.core.grpc.server.instantiateRequestStateInterceptor')
@patch('khaleesi.core.grpc.server.LOGGER')
@patch('khaleesi.core.grpc.server.HEALTH_METRIC')
@patch('khaleesi.core.grpc.server.MetricInitializer')
@patch('khaleesi.core.grpc.server.stopAllJobs')
@patch('khaleesi.core.grpc.server.CHANNEL_MANAGER')
@patch('khaleesi.core.grpc.server.SINGLETON')
@patch('khaleesi.core.grpc.server.server')
class ServerTestCase(SimpleTestCase):
  """Test the gRPC server."""

  def testInitializationSuccess(self, *_: MagicMock) -> None :
    """Test initialization success."""
    # Execute test & assert result.
    Server(startHttpRequestId = 'http-request-id', initializeGrpcRequestId = 'grpc-request-id')

  def testInitializationKhaleesiFailure(
      self,
      grpcServer: MagicMock,
      singleton : MagicMock,
      *_        : MagicMock,
  ) -> None :
    """Test initialization failure."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          exception = defaultKhaleesiException(status = status, loglevel = loglevel)
          grpcServer.side_effect = exception
          # Execute test.
          with self.assertRaises(KhaleesiException):
            Server(
              startHttpRequestId      = 'http-request-id',
              initializeGrpcRequestId = 'grpc-request-id',
            )
          # Assert result.
          self._assertServerStateEvent(
            action    = Event.Action.ActionType.START,
            result    = Event.Action.ResultType.FATAL,
            singleton = singleton,
          )
          self._assertExceptionLogging(
            singleton = singleton,
            exception = exception,
            loglevel  = loglevel,
          )

  def testInitializationOtherFailure(
      self,
      grpcServer: MagicMock,
      singleton : MagicMock,
      *_        : MagicMock,
  ) -> None :
    """Test initialization failure."""
    # Prepare data.
    grpcServer.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      Server(startHttpRequestId = 'http-request', initializeGrpcRequestId = 'grpc-request')
    # Assert result.
    self._assertServerStateEvent(
      action    = Event.Action.ActionType.START,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )

  def testSigtermSuccess(self,
      grpcServer    : MagicMock,
      singleton     : MagicMock,
      channelManager: MagicMock,
      threadsToStop : MagicMock,
      *_            : MagicMock,
  ) -> None :
    """Test sigterm success."""
    # Prepare data.
    server = Server(
      startHttpRequestId      = 'http-request-id',
      initializeGrpcRequestId = 'grpc-request-id',
    )
    event = threading.Event()
    grpcServer.return_value.stop.return_value = event
    threadsToStop.return_value = []
    # Execute test.
    event.set()
    server._handleSigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assertServerStateEvent(
      action    = Event.Action.ActionType.END,
      result    = Event.Action.ResultType.SUCCESS,
      singleton = singleton,
    )
    singleton.structuredLogger.logHttpRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcResponse.assert_called_once()
    singleton.structuredLogger.logHttpResponse.assert_called_once()
    channelManager.closeAllChannels.assert_called_once_with()

  def testSigtermFailureServerTimeout(
      self,
      grpcServer    : MagicMock,
      singleton     : MagicMock,
      channelManager: MagicMock,
      threadsToStop : MagicMock,
      *_            : MagicMock,
  ) -> None :
    """Test sigterm failure."""
    # Prepare data.
    server = Server(
      startHttpRequestId      = 'http-request-id',
      initializeGrpcRequestId = 'grpc-request-id',
    )
    grpcServer.return_value.stop.side_effect = Exception('test')
    threadsToStop.return_value = []
    # Execute test.
    with self.assertRaises(Exception):
      server._handleSigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assertServerStateEvent(
      action    = Event.Action.ActionType.END,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )
    singleton.structuredLogger.logHttpRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcResponse.assert_called_once()
    singleton.structuredLogger.logHttpResponse.assert_called_once()
    channelManager.closeAllChannels.assert_called_once_with()

  def testSigtermFailureThreadTimeout(
      self,
      grpcServer    : MagicMock,
      singleton     : MagicMock,
      channelManager: MagicMock,
      threadsToStop : MagicMock,
      *_            : MagicMock,
  ) -> None :
    """Test sigterm failure."""
    # Prepare data.
    server = Server(
      startHttpRequestId      = 'http-request-id',
      initializeGrpcRequestId = 'grpc-request-id',
    )
    event = threading.Event()
    grpcServer.return_value.stop.return_value = event
    threadToStop = MagicMock()
    threadToStop.is_alive.return_value = False
    threadsToStop.return_value = [ threadToStop ]
    # Execute test.
    event.set()
    with self.assertRaises(Exception):
      server._handleSigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assertServerStateEvent(
      action    = Event.Action.ActionType.END,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )
    singleton.structuredLogger.logHttpRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcResponse.assert_called_once()
    singleton.structuredLogger.logHttpResponse.assert_called_once()
    channelManager.closeAllChannels.assert_called_once_with()

  def testSigtermTimeout(
      self,
      grpcServer    : MagicMock,
      singleton     : MagicMock,
      channelManager: MagicMock,
      *_            : MagicMock,
  ) -> None :
    """Test sigterm timeout."""
    # Prepare data.
    server = Server(
      startHttpRequestId      = 'http-request-id',
      initializeGrpcRequestId = 'grpc-request-id',
    )
    event = threading.Event()
    grpcServer.return_value.stop.return_value = event
    # Execute test.
    with self.assertRaises(TimeoutException):
      server._handleSigterm()  # pylint: disable=protected-access
    # Assert result.
    self._assertServerStateEvent(
      action    = Event.Action.ActionType.END,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )
    singleton.structuredLogger.logHttpRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcRequest.assert_called_once()
    singleton.structuredLogger.logSystemGrpcResponse.assert_called_once()
    singleton.structuredLogger.logHttpResponse.assert_called_once()
    channelManager.closeAllChannels.assert_called_once_with()

  def testStart(self, grpcServer: MagicMock, singleton: MagicMock, *_: MagicMock) -> None :
    """Test that server start works correctly."""
    # Prepare data.
    server = Server(
      startHttpRequestId      = 'http-request-id',
      initializeGrpcRequestId = 'grpc-request-id',
    )
    # Execute test.
    server.start(startGrpcRequestId = 'grpc-request-id')
    # Assert result.
    grpcServer.return_value.start.assert_called_once_with()
    self._assertServerStateEvent(
      action    = Event.Action.ActionType.START,
      result    = Event.Action.ResultType.SUCCESS,
      singleton = singleton,
    )

  def testWaitForTermination(self, grpcServer: MagicMock, *_: MagicMock) -> None :
    """Test that server wait for termination works correctly."""
    # Prepare data.
    server = Server(
      startHttpRequestId      = 'http-request-id',
      initializeGrpcRequestId = 'grpc-request-id',
    )
    # Execute test.
    server.waitForTermination()
    # Assert result.
    grpcServer.return_value.wait_for_termination.assert_called_once_with()

  def testStartKhaleesiFailure(
      self,
      grpcServer: MagicMock,
      singleton : MagicMock,
      *_        : MagicMock,
  ) -> None :
    """Test that server start fails correctly."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          exception = defaultKhaleesiException(status = status, loglevel = loglevel)
          server = Server(
            startHttpRequestId      = 'http-request-id',
            initializeGrpcRequestId = 'grpc-request-id',
          )
          grpcServer.return_value.start.side_effect = exception
          # Execute test.
          with self.assertRaises(KhaleesiException):
            server.start(startGrpcRequestId = 'grpc-request-id')
          # Assert result.
          self._assertServerStateEvent(
            action    = Event.Action.ActionType.START,
            result    = Event.Action.ResultType.FATAL,
            singleton = singleton,
          )
          self._assertExceptionLogging(
            singleton = singleton,
            exception = exception,
            loglevel  = loglevel,
          )

  def testStartOtherFailure(
      self,
      grpcServer: MagicMock,
      singleton : MagicMock,
      *_        : MagicMock,
  ) -> None :
    """Test that server start fails correctly."""
    # Prepare data.
    server = Server(
      startHttpRequestId      = 'http-request-id',
      initializeGrpcRequestId = 'grpc-request-id',
    )
    grpcServer.return_value.start.side_effect = Exception('test')
    # Execute test.
    with self.assertRaises(Exception):
      server.start(startGrpcRequestId = 'grpc-request-id')
    # Assert result.
    self._assertServerStateEvent(
      action    = Event.Action.ActionType.START,
      result    = Event.Action.ResultType.FATAL,
      singleton = singleton,
    )

  def _assertExceptionLogging(
      self, *,
      singleton: MagicMock,
      exception: KhaleesiException,
      loglevel : LogLevel,
  ) -> None :
    """Assert exception logging."""
    loggedException = cast(
      KhaleesiException,
      singleton.structuredLogger.logSystemError.call_args.kwargs['exception'],
    )
    self.assertEqual(exception.status  , loggedException.status)
    self.assertEqual(exception.loglevel, loglevel)
    self.assertEqual(exception.loglevel, loggedException.loglevel)

  def _assertServerStateEvent(
      self, *,
      action   : 'Event.Action.ActionType.V',
      result   : 'Event.Action.ResultType.V',
      singleton: MagicMock,
  ) -> None :
    """Assert the result."""
    kwargs = singleton.structuredLogger.logSystemEvent.call_args.kwargs
    self.assertEqual(kwargs['method']                 , 'LIFECYCLE')
    self.assertEqual(kwargs['event'].target.owner.type, User.UserType.SYSTEM)
    self.assertEqual(kwargs['event'].action.crudType  , action)
    self.assertEqual(kwargs['event'].action.result    , result)
