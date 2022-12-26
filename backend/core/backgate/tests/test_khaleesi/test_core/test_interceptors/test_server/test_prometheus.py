"""Test PrometheusServerInterceptor."""

# pylint: disable=duplicate-code

# Python.
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.logging.text_logger import LogLevel
from khaleesi.core.test_util.exceptions import khaleesi_raising_method, exception_raising_method
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


class PrometheusServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test PrometheusServerInterceptor."""

  interceptor = PrometheusServerInterceptor()

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
        self._execute_intercept_khaleesi_exception_test,
        self._execute_intercept_other_exception_test,
    ]:
      for user_label, user_type in User.UserType.items():
        with self.subTest(test = test.__name__, user = user_label):
          request_metadata, final_request = self.get_request(
            request = request,
            user = user_type,
            **request_params,
          )
          test(request_metadata = request_metadata, final_request = final_request)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.server.prometheus.INCOMING_REQUESTS')
  def _execute_intercept_ok_test(
      self,
      metric: MagicMock,
      *,
      request_metadata: RequestMetadata,
      final_request: Any,
  ) -> None :
    """Test the counter gets incremented."""
    # Execute test.
    self.interceptor.khaleesi_intercept(request = final_request, **self.get_intercept_params())
    # Assert result.
    self._assert_metric_call(
      metric           = metric,
      request_metadata = request_metadata,
      status           = StatusCode.OK,
    )

  @patch('khaleesi.core.interceptors.server.prometheus.INCOMING_REQUESTS')
  def _execute_intercept_khaleesi_exception_test(
      self,
      metric: MagicMock,
      *,
      request_metadata: RequestMetadata,
      final_request: Any,
  ) -> None :
    """Test the counter gets incremented."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          metric.reset_mock()
          # Execute test.
          with self.assertRaises(KhaleesiException):
            self.interceptor.khaleesi_intercept(
              request = final_request,
              **self.get_intercept_params(
                method = khaleesi_raising_method(status = status, loglevel = loglevel),
              ),
            )
          # Assert result.
          self._assert_metric_call(
            metric           = metric,
            request_metadata = request_metadata,
            status           = status,
          )

  @patch('khaleesi.core.interceptors.server.prometheus.INCOMING_REQUESTS')
  def _execute_intercept_other_exception_test(
      self,
      metric: MagicMock,
      *,
      request_metadata: RequestMetadata,
      final_request: Any,
  ) -> None :
    """Test the counter gets incremented."""
    # Execute test.
    with self.assertRaises(Exception):
      self.interceptor.khaleesi_intercept(
        request = final_request,
        **self.get_intercept_params(method = exception_raising_method()),
      )
    # Assert result.
    self._assert_metric_call(
      metric           = metric,
      request_metadata = request_metadata,
      status           = StatusCode.UNKNOWN,
    )

  def _assert_metric_call(
      self, *,
      metric: MagicMock,
      request_metadata: RequestMetadata,
      status: StatusCode,
  ) -> None :
    """Assert the metric call was correct."""
    metric.inc.assert_called_once()
    self.assertEqual(status          , metric.inc.call_args.kwargs['status'])
    self.assertEqual(request_metadata, metric.inc.call_args.kwargs['peer'])
