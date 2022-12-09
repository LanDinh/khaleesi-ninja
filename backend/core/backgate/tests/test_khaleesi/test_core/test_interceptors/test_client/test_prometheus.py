"""Test PrometheusClientInterceptor"""

# pylint: disable=duplicate-code

# Python.
from functools import partial
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.client.prometheus import PrometheusClientInterceptor
from khaleesi.core.test_util.interceptor import ClientInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


class PrometheusClientInterceptorTest(ClientInterceptorTestMixin, SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = PrometheusClientInterceptor()

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
    for test in [ self._execute_intercept_test ]:
      for user_label, user_type in User.UserType.items():
        with self.subTest(test = test.__name__, user = user_label):
          request_metadata, final_request = self.get_request(
            request = request,
            user = user_type,
            **request_params,
          )
          test(request_metadata = request_metadata, final_request = final_request)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.client.prometheus.OUTGOING_REQUESTS')
  def _execute_intercept_test(
      self,
      metric: MagicMock,
      *,
      request_metadata: RequestMetadata,
      final_request: Any,
  ) -> None :
    """Test the counter gets incremented."""
    for code in StatusCode:
      with self.subTest(code = code):
        # Prepare data.
        metric.reset_mock()
        response = MagicMock()
        response.code = MagicMock(return_value = code)
        # Execute test.
        self.interceptor.khaleesi_intercept(
          request_or_iterator = final_request,
          **self.get_intercept_params(method = partial(
            lambda inner_response, *args : inner_response,
            response,
          )),
        )
        # Assert result.
        self._assert_metric_call(
          metric           = metric,
          request_metadata = request_metadata,
          status           = code,
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
    self.assertEqual(request_metadata, metric.inc.call_args.kwargs['request'])
