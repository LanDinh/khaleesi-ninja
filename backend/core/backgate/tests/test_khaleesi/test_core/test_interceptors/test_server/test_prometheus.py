"""Test PrometheusServerInterceptor"""

# Python.
from functools import partial
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.exceptions import KhaleesiException
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


def _raise(exception: Exception) -> None :
  """Helper to raise exceptions in lambdas."""
  raise exception


class PrometheusServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = PrometheusServerInterceptor()

  def test_intercept_with_request_metadata(self) -> None :
    """Test intercept with metadata present."""
    for name, request_params in self.metadata_request_params:
      with self.subTest(case = name):
        self._execute_intercept_tests(request_params = request_params)  # type: ignore[arg-type]

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
      with self.subTest(status = status.name):
        # Prepare data.
        metric.reset_mock()
        exception = KhaleesiException(
          status          = status,
          gate            = 'gate',
          service         = 'service',
          public_key      = 'public-key',
          public_details  = 'public-details',
          private_details = 'private-details',
        )
        # Execute test.
        with self.assertRaises(KhaleesiException):
          # noinspection PyTypeChecker
          self.interceptor.khaleesi_intercept(request = final_request, **self.get_intercept_params(
            method  = partial(
              lambda inner_exception, *args : _raise(inner_exception),
              exception,
            ),
          ))
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
        **self.get_intercept_params(method  = lambda *args : _raise(Exception('exception'))),
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
    metric.inc.assert_called_once_with(
      status           = status,
      request_metadata = request_metadata,
      grpc_service     = self.service_name,
      grpc_method      = self.method_name,
    )
