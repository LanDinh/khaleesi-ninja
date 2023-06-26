"""Test LoggingClientInterceptor"""

# pylint: disable=duplicate-code

# Python.
from functools import partial
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import UpstreamGrpcException
from khaleesi.core.interceptors.client.logging import LoggingClientInterceptor
from khaleesi.core.testUtil.interceptor import ClientInterceptorTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User


class LoggingClientInterceptorTest(ClientInterceptorTestMixin, SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = LoggingClientInterceptor()

  def testInterceptWithRequestMetadata(self) -> None :
    """Test intercept with metadata present."""
    for name, requestParams in self.metadataRequestParams:
      with self.subTest(case = name):
        self._executeInterceptTests(requestParams = requestParams)

  def testInterceptWithoutRequestMetadata(self) -> None :
    """Test intercept with no metadata present."""
    self._executeInterceptTests(request = {}, requestParams = self.emptyInput)

  def _executeInterceptTests(
      self, *,
      request      : Optional[Any] = None,
      requestParams: Dict[str, Any],
  ) -> None :
    """Execute all typical intercept tests."""
    for test in [
        self._executeInterceptOkTest,
        self._executeInterceptNotOkTest,
    ]:
      for userLabel, userType in User.UserType.items():
        with self.subTest(test = test.__name__, user = userLabel):
          _, finalRequest = self.getRequest(
            request = request,
            user    = userType,
            **requestParams,
          )
          test(finalRequest = finalRequest)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.client.logging.LOGGER')
  def _executeInterceptOkTest(
      self,
      logger: MagicMock,
      *,
      finalRequest: Any,
  ) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    response = MagicMock()
    response.code = MagicMock(return_value = StatusCode.OK)
    # Execute test.
    self.interceptor.khaleesiIntercept(
      requestOrIterator = finalRequest,
      **self.getInterceptParams(method = lambda *args : response),
    )
    # Assert result.
    self.assertEqual(2, logger.info.call_count)

  @patch('khaleesi.core.interceptors.client.logging.LOGGER')
  def _executeInterceptNotOkTest(
      self,
      logger: MagicMock,
      *,
      finalRequest: Any,
  ) -> None :
    """Test the counter gets incremented."""
    for code in [code for code in StatusCode if code != StatusCode.OK]:
      for exception in [None, Exception('test')]:
        with self.subTest(code = code, exception = exception):
          # Prepare data.
          logger.reset_mock()
          response = MagicMock()
          response.code = MagicMock(return_value = code)
          response.exception.return_value = exception
          # Execute test.
          with self.assertRaises(UpstreamGrpcException):
            self.interceptor.khaleesiIntercept(
              requestOrIterator = finalRequest,
              **self.getInterceptParams(method = partial(
                lambda innerResponse, *args : innerResponse,
                response,
              )),
            )
          # Assert result.
          logger.info.assert_called_once()
          logger.warning.assert_called_once()
