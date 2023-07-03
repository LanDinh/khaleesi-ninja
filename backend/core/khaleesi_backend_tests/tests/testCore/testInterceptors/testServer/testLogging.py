"""Test LoggingServerInterceptor"""

# Python.
from typing import Any, Dict, Optional, cast
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.logging import (
  LoggingServerInterceptor,
  instantiateLoggingInterceptor,
)
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.exceptions import (
  khaleesiRaisingMethod,
  defaultKhaleesiException,
  exceptionRaisingMethod,
  defaultException,
)
from khaleesi.core.testUtil.interceptor import ServerInterceptorTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


@patch('khaleesi.core.interceptors.server.logging.SINGLETON')
class LoggingServerInterceptorTestCase(ServerInterceptorTestMixin, SimpleTestCase):
  """Test LoggingServerInterceptor"""

  interceptor = LoggingServerInterceptor()

  def testInterceptWithRequestMetadata(self, singleton: MagicMock) -> None :
    """Test intercept with metadata present."""
    for name, requestParams in self.metadataRequestParams:
      with self.subTest(case = name):
        self._executeInterceptGrpcLoggingTest(
          requestParams = requestParams,
          singleton     = singleton,
        )

  def testInterceptWithoutRequestMetadata(self, singleton: MagicMock) -> None :
    """Test intercept with no metadata present."""
    self._executeInterceptGrpcLoggingTest(
      request       = {},
      requestParams = self.emptyInput,
      singleton     = singleton,
    )

  def testLoggingKhaleesiException(self, singleton: MagicMock) -> None :
    """Test the counter gets incremented."""
    for userLabel, userType in User.UserType.items():
      for status in StatusCode:
        for loglevel in LogLevel:
          with self.subTest(user = userLabel, status = status.name, loglevel = loglevel.name):
            # Prepare data.
            _, finalRequest = self.getRequest(
              request       = {},
              user          = userType,
              requestParams = self.emptyInput,
            )
            STATE.reset()
            exception = defaultKhaleesiException(status = status, loglevel = loglevel)
            # Execute test.
            with self.assertRaises(KhaleesiException):
              self.interceptor.khaleesiIntercept(
                request = finalRequest,
                **self.getInterceptParams(
                  method = khaleesiRaisingMethod(status = status, loglevel = loglevel),
                ),
              )
            # Assert result.
            self._assertExceptionLoggingCall(
              loglevel  = loglevel,
              exception = exception,
              singleton = singleton,
            )

  def testLoggingOtherException(self, singleton: MagicMock) -> None :
    """Test the counter gets incremented."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel.lower()):
        # Prepare data.
        _, finalRequest = self.getRequest(
          request       = {},
          user          = userType,
          requestParams = self.emptyInput,
        )
        STATE.reset()
        exception = defaultException()
        # Execute test.
        with self.assertRaises(KhaleesiException):
          self.interceptor.khaleesiIntercept(
            request = finalRequest,
            **self.getInterceptParams(method = exceptionRaisingMethod(exception = exception)),
          )
        # Assert result.
        self._assertExceptionLoggingCall(
          loglevel  = LogLevel.FATAL,
          exception = MaskingInternalServerException(exception = exception),
          singleton = singleton,
        )

  def _executeInterceptGrpcLoggingTest(
      self, *,
      request       : Optional[Any] = None,
      requestParams: Dict[str, Any],
      singleton     : MagicMock,
  ) -> None :
    """Execute the logging tests."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel.lower()):
        # Prepare data.
        requestMetadata, finalRequest = self.getRequest(
          request = request,
          user    = userType,
          **requestParams,
        )
        context = MagicMock()
        STATE.reset()
        # Execute test.
        self.interceptor.khaleesiIntercept(
          request = finalRequest,
          **self.getInterceptParams(context = context),
        )
        # Assert result.
        self._assertLoggingCall(
          context         = context,
          requestMetadata = requestMetadata,
          singleton       = singleton
        )

  def _assertLoggingCall(
      self, *,
      context        : MagicMock,
      requestMetadata: RequestMetadata,
      singleton      : MagicMock,
  ) -> None :
    """Assert the logging calls were correct."""
    upstreamRequest = cast(
      RequestMetadata,
      singleton.structuredLogger.logGrpcRequest.call_args.kwargs['upstreamRequest'],
    )
    status = cast(
      StatusCode,
      singleton.structuredLogger.logGrpcResponse.call_args.kwargs['status'],
    )
    context.set_code.assert_not_called()
    context.set_details.assert_not_called()
    self.assertEqual(requestMetadata.grpcCaller, upstreamRequest.grpcCaller)
    self.assertEqual(StatusCode.OK             , status)

  def _assertExceptionLoggingCall(
      self, *,
      exception: KhaleesiException,
      loglevel : LogLevel,
      singleton: MagicMock,
  ) -> None :
    """Assert the logging calls were correct."""
    status = cast(
      StatusCode,
      singleton.structuredLogger.logGrpcResponse.call_args.kwargs['status'],
    )
    loggedException = cast(
      KhaleesiException,
      singleton.structuredLogger.logError.call_args.kwargs['exception'],
    )
    self.assertEqual(exception.status        , status)
    self.assertEqual(exception.status        , loggedException.status)
    self.assertEqual(exception.loglevel      , loglevel)
    self.assertEqual(exception.loglevel      , loggedException.loglevel)
    self.assertEqual(exception.gate          , loggedException.gate)
    self.assertEqual(exception.service       , loggedException.service)
    self.assertEqual(exception.publicKey     , loggedException.publicKey)
    self.assertEqual(exception.publicDetails , loggedException.publicDetails)
    self.assertEqual(exception.privateMessage, loggedException.privateMessage)
    self.assertEqual(exception.privateDetails, loggedException.privateDetails)
    self.assertIsNotNone(loggedException.stacktrace)


class LoggingServerInterceptorInstantiationTest(SimpleTestCase):
  """Test instantiation."""

  def testInstantiation(self) -> None :
    """Test instantiation."""
    # Execute test & assert result.
    instantiateLoggingInterceptor()
