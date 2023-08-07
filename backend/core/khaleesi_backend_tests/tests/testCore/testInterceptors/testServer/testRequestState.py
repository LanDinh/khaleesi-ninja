"""Test RequestStateServerInterceptor."""

# Python.
from functools import partial
from typing import Optional, Any, Dict
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.requestState import (
  RequestStateServerInterceptor,
  instantiateRequestStateInterceptor
)
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.exceptions import khaleesiRaisingMethod
from khaleesi.core.testUtil.interceptor import ServerInterceptorTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User


@patch('khaleesi.core.interceptors.server.requestState.LOGGER')
class RequestStateServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test RequestStateServerInterceptor."""

  interceptor = RequestStateServerInterceptor()

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
        _, finalRequest = self.getRequest(request = request, user = userType, **requestParams)  # type: ignore[arg-type]  # pylint: disable=line-too-long
        test(finalRequest = finalRequest, userType = userType)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.server.requestState.queryLogger')
  def _executeInterceptOkTest(
      self,
      queryLogger: MagicMock,
      *,
      finalRequest: Any,
      userType    : int,
  ) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    def _method(*_: Any) -> None :
      self._assertNotCleanState(userType = userType)
    # Execute test.
    self.interceptor.khaleesiIntercept(
      request = finalRequest,
      **self.getInterceptParams(executableMethod = _method),
    )
    # Assert result.
    self._assertCleanState()
    queryLogger.assert_called_once()

  @patch('khaleesi.core.interceptors.server.requestState.queryLogger')
  def _executeInterceptKhaleesiExceptionTest(
      self,
      queryLogger: MagicMock,
      *,
      finalRequest: Any,
      userType    : int,
  ) -> None :
    """Test the counter gets incremented."""
    context = MagicMock()
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          queryLogger.reset_mock()
          context.reset_mock()
          # Execute test.
          self.interceptor.khaleesiIntercept(
            request = finalRequest,
            **self.getInterceptParams(
              context = context,
              executableMethod = khaleesiRaisingMethod(
                method   = partial(self._assertNotCleanState, userType = userType),
                status   = status,
                loglevel = loglevel,
              ),
            ),
          )
          # Assert result.
          self._assertCleanState()
          context.abort.assert_called_once()
          queryLogger.assert_called_once()

  @patch('khaleesi.core.interceptors.server.requestState.queryLogger')
  def _executeInterceptOtherExceptionTest(
      self,
      queryLogger: MagicMock,
      *,
      finalRequest: Any,
      userType    : int,
  ) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    context = MagicMock()
    def _method(*_: Any) -> None :
      self._assertNotCleanState(userType = userType)
      raise Exception('exception')  # pylint: disable=broad-exception-raised
    # Execute test.
    self.interceptor.khaleesiIntercept(
      request = finalRequest,
      **self.getInterceptParams(context = context, executableMethod = _method),
    )
    # Assert result.
    self._assertCleanState()
    context.abort.assert_called_once()
    queryLogger.assert_called_once()

  def _assertCleanState(self) -> None :
    """Assert a clean state."""
    self.assertEqual('UNKNOWN', STATE.request.httpCaller.requestId)
    self.assertEqual('system' , STATE.request.grpcCaller.requestId)
    self.assertEqual('UNKNOWN', STATE.request.user.id)
    self.assertEqual(User.UserType.UNKNOWN, STATE.request.user.type)

  # noinspection PyUnusedLocal
  def _assertNotCleanState(self, *args: Any, userType: int, **kwargs: Any) -> None :
    """Assert a clean state."""
    self.assertNotEqual('UNKNOWN', STATE.request.httpCaller.requestId)
    self.assertNotEqual('system' , STATE.request.grpcCaller.requestId)
    self.assertNotEqual('UNKNOWN', STATE.request.user.id)
    self.assertEqual(userType, STATE.request.user.type)


class RequestStateServerInterceptorInstantiationTest(SimpleTestCase):
  """Test instantiation."""

  def testInstantiation(self) -> None :
    """Test instantiation."""
    # Execute test.
    instantiateRequestStateInterceptor()
