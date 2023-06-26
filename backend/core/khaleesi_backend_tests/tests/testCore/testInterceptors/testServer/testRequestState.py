"""Test RequestStateServerInterceptor."""

# Python.
from functools import partial
from typing import Optional, Any, Dict
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.requestState import (
  BaseRequestStateServerInterceptor,
  RequestStateServerInterceptor,
  instantiateRequestStateInterceptor
)
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.core.testUtil.exceptions import khaleesiRaisingMethod
from khaleesi.core.testUtil.interceptor import ServerInterceptorTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata


class RequestStateServerTestInterceptor(BaseRequestStateServerInterceptor):
  """Subclass to test base functionality."""

  mock = MagicMock()

  def setHttpRequestId(self, *, upstream: RequestMetadata) -> None :
    """Set the HTTP request."""
    self.mock()


@patch('khaleesi.core.interceptors.server.requestState.LOGGER')
class BaseRequestStateServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test RequestStateServerInterceptor."""

  interceptor = RequestStateServerTestInterceptor()

  def testInterceptWithRequestMetadata(self, *_: MagicMock) -> None :
    """Test intercept with metadata present."""
    for name, requestParams in self.metadataRequestParams:
      for userLabel, userType in User.UserType.items():
        with self.subTest(case = name, user = userLabel):
          self._executeInterceptTests(requestParams = requestParams, userType = userType)

  def testInterceptWithoutRequestMetadata(self, *_: MagicMock) -> None :
    """Test intercept with no metadata present."""
    self._executeInterceptTests(
      request       = {},
      requestParams = self.emptyInput,
      userType      = User.UserType.UNKNOWN,
    )

  def _executeInterceptTests(
      self, *,
      request      : Optional[Any] = None,
      requestParams: Dict[str, Any],
      userType     : int,
  ) -> None :
    """Execute all typical intercept tests."""
    for test in [
        self._executeInterceptOkTest,
        self._executeInterceptKhaleesiExceptionTest,
        self._executeInterceptOtherExceptionTest,
    ]:
      with self.subTest(test = test.__name__):
        _, finalRequest = self.getRequest(
          request = request,
          user    = userType,  # type: ignore[arg-type]
          **requestParams,
        )
        test(finalRequest = finalRequest, userType = userType)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.server.requestState.queryLogger')
  def _executeInterceptOkTest(
      self,
      queryLogger: MagicMock,
      *,
      finalRequest: Any,
      userType: int,
  ) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    self.interceptor.mock.reset_mock()
    def _method(*_: Any) -> None :
      self._assertNotCleanState(userType = userType)
    # Execute test.
    self.interceptor.khaleesiIntercept(
      request = finalRequest,
      **self.getInterceptParams(method = _method),
    )
    # Assert result.
    self._assertCleanState()
    self.interceptor.mock.assert_called_once()
    queryLogger.assert_called_once()

  @patch('khaleesi.core.interceptors.server.requestState.queryLogger')
  def _executeInterceptKhaleesiExceptionTest(
      self,
      queryLogger: MagicMock,
      *,
      finalRequest: Any,
      userType: int,
  ) -> None :
    """Test the counter gets incremented."""
    context = MagicMock()
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          self.interceptor.mock.reset_mock()
          queryLogger.reset_mock()
          context.reset_mock()
          # Execute test.
          self.interceptor.khaleesiIntercept(
            request = finalRequest,
            **self.getInterceptParams(
              context = context,
              method  = khaleesiRaisingMethod(
                method   = partial(self._assertNotCleanState, userType = userType),
                status   = status,
                loglevel = loglevel,
              ),
            ),
          )
          # Assert result.
          self._assertCleanState()
          self.interceptor.mock.assert_called_once()
          context.abort.assert_called_once()
          queryLogger.assert_called_once()

  @patch('khaleesi.core.interceptors.server.requestState.queryLogger')
  def _executeInterceptOtherExceptionTest(
      self,
      queryLogger: MagicMock,
      *,
      finalRequest: Any,
      userType: int,
  ) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    context = MagicMock()
    self.interceptor.mock.reset_mock()
    def _method(*_: Any) -> None :
      self._assertNotCleanState(userType = userType)
      raise Exception('exception')
    # Execute test.
    self.interceptor.khaleesiIntercept(
      request = finalRequest,
      **self.getInterceptParams(context = context, method = _method),
    )
    # Assert result.
    self._assertCleanState()
    context.abort.assert_called_once()
    self.interceptor.mock.assert_called_once()
    queryLogger.assert_called_once()

  def _assertCleanState(self) -> None :
    """Assert a clean state."""
    self.assertEqual('UNKNOWN'       , STATE.request.grpcService)
    self.assertEqual('UNKNOWN'       , STATE.request.grpcMethod)
    self.assertEqual('UNKNOWN'       , STATE.user.userId)
    self.assertEqual(UserType.UNKNOWN, STATE.user.type)

  # noinspection PyUnusedLocal
  def _assertNotCleanState(self, *args: Any, userType: int, **kwargs: Any) -> None :
    """Assert a clean state."""
    self.assertNotEqual('UNKNOWN'      , STATE.request.grpcService)
    self.assertNotEqual('UNKNOWN'      , STATE.request.grpcMethod)
    self.assertNotEqual('UNKNOWN'      , STATE.user.userId)
    self.assertEqual(UserType(userType), STATE.user.type)


class RequestStateServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test RequestStateServerInterceptor."""

  interceptor = RequestStateServerInterceptor()

  def testSetHttpRequestIdWithRequestMetadata(self) -> None :
    """Test setting the HTTP request id."""
    for name, requestParams in self.metadataRequestParams:
      for userLabel, userType in User.UserType.items():
        with self.subTest(case = name, user = userLabel):
          # Prepare data.
          requestMetadata, _ = self.getRequest(
            request = None,
            user    = userType,
            **requestParams,
          )
          STATE.reset()
          # Execute test.
          self.interceptor.setHttpRequestId(upstream = requestMetadata)
          # Assert result.
          self.assertEqual(requestMetadata.caller.httpRequestId, STATE.request.httpRequestId)


class RequestStateServerInterceptorInstantiationTest(SimpleTestCase):
  """Test instantiation."""

  @patch('khaleesi.core.interceptors.server.requestState.LOGGER')
  @patch('khaleesi.core.interceptors.server.requestState.importSetting')
  def testInstantiation(self, importSetting: MagicMock, *_: MagicMock) -> None :
    """Test instantiation."""
    # Execute test.
    instantiateRequestStateInterceptor()
    # Assert result.
    importSetting.assert_called_once()
