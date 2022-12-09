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
from khaleesi.core.test_util.interceptor import ClientInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User


class LoggingClientInterceptorTest(ClientInterceptorTestMixin, SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = LoggingClientInterceptor()

  def test_intercept_with_request_metadata(self) -> None :
    """Test intercept with metadata present."""
    for name, request_params in self.metadata_request_params:
      with self.subTest(case = name):
        self._execute_intercept_tests(request_params = request_params)

  def test_intercept_without_request_metadata(self) -> None :
    """Test intercept with no metadata present."""
    self._execute_intercept_tests(request = {}, request_params = self.empty_input)

  def _execute_intercept_tests(
      self, *,
      request: Optional[Any] = None,
      request_params: Dict[str, Any],
  ) -> None :
    """Execute all typical intercept tests."""
    for test in [
        self._execute_intercept_ok_test,
        self._execute_intercept_not_ok_test,
    ]:
      for user_label, user_type in User.UserType.items():
        with self.subTest(test = test.__name__, user = user_label):
          _, final_request = self.get_request(
            request = request,
            user = user_type,
            **request_params,
          )
          test(final_request = final_request)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.client.logging.LOGGER')
  def _execute_intercept_ok_test(
      self,
      logger: MagicMock,
      *,
      final_request: Any,
  ) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    response = MagicMock()
    response.code = MagicMock(return_value = StatusCode.OK)
    # Execute test.
    self.interceptor.khaleesi_intercept(
      request_or_iterator = final_request,
      **self.get_intercept_params(method = lambda *args : response),
    )
    # Assert result.
    self.assertEqual(2, logger.info.call_count)

  @patch('khaleesi.core.interceptors.client.logging.LOGGER')
  def _execute_intercept_not_ok_test(
      self,
      logger: MagicMock,
      *,
      final_request: Any,
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
            self.interceptor.khaleesi_intercept(
              request_or_iterator = final_request,
              **self.get_intercept_params(method = partial(
                lambda inner_response, *args : inner_response,
                response,
              )),
            )
          # Assert result.
          logger.info.assert_called_once()
          logger.warning.assert_called_once()
