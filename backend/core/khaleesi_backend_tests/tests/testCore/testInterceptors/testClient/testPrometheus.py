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
from khaleesi.core.testUtil.interceptor import ClientInterceptorTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


class PrometheusClientInterceptorTest(ClientInterceptorTestMixin, SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = PrometheusClientInterceptor()

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
    for test in [ self._executeInterceptTest ]:
      for userLabel, userType in User.UserType.items():
        with self.subTest(test = test.__name__, user = userLabel):
          requestMetadata, finalRequest = self.getRequest(
            request = request,
            user    = userType,
            **requestParams,
          )
          test(requestMetadata = requestMetadata, finalRequest = finalRequest)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.client.prometheus.OUTGOING_REQUESTS')
  def _executeInterceptTest(
      self,
      metric: MagicMock,
      *,
      requestMetadata: RequestMetadata,
      finalRequest: Any,
  ) -> None :
    """Test the counter gets incremented."""
    for code in StatusCode:
      with self.subTest(code = code):
        # Prepare data.
        metric.reset_mock()
        response = MagicMock()
        response.code = MagicMock(return_value = code)
        # Execute test.
        self.interceptor.khaleesiIntercept(
          requestOrIterator = finalRequest,
          **self.getInterceptParams(method = partial(
            lambda innerResponse, *args : innerResponse,
            response,
          )),
        )
        # Assert result.
        self._assertMetricCall(
          metric          = metric,
          requestMetadata = requestMetadata,
          status          = code,
        )

  def _assertMetricCall(
      self, *,
      metric: MagicMock,
      requestMetadata: RequestMetadata,
      status: StatusCode,
  ) -> None :
    """Assert the metric call was correct."""
    metric.inc.assert_called_once()
    self.assertEqual(status         , metric.inc.call_args.kwargs['status'])
    self.assertEqual(requestMetadata, metric.inc.call_args.kwargs['request'])
