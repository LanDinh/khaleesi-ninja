"""Test PrometheusServerInterceptor."""

# pylint: disable=duplicate-code

# Python.
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.prometheus import (
  PrometheusServerInterceptor,
  instantiatePrometheusInterceptor,
)
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.testUtil.exceptions import khaleesiRaisingMethod, exceptionRaisingMethod
from khaleesi.core.testUtil.interceptor import ServerInterceptorTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


class PrometheusServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test PrometheusServerInterceptor."""

  interceptor = PrometheusServerInterceptor()

  def testInterceptWithRequestMetadata(self) -> None :
    """Test intercept with metadata present."""
    for name, requestParams in self.metadataRequestParams:
      with self.subTest(case = name):
        self._executeInterceptTests(requestParams = requestParams)

  def testInterceptWithoutRequestMetadata(self) -> None :
    """Test intercept with no metadata present."""
    self._executeInterceptTests(request = {}, requestParams = self.emptyInput)

  def testInstantiation(self) -> None :
    """Test instantiation."""
    # Execute test.
    instantiatePrometheusInterceptor()

  def _executeInterceptTests(
      self, *,
      request: Optional[Any] = None,
      requestParams: Dict[str, Any],
  ) -> None :
    """Execute all typical intercept tests."""
    for test in [
        self._executeInterceptOkTest,
        self._executeInterceptKhaleesiExceptionTest,
        self._executeInterceptOtherExceptionTest,
    ]:
      for userLabel, userType in User.UserType.items():
        with self.subTest(test = test.__name__, user = userLabel):
          requestMetadata, finalRequest = self.getRequest(
            request = request,
            user    = userType,
            **requestParams,
          )
          test(requestMetadata = requestMetadata, finalRequest = finalRequest)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.server.prometheus.INCOMING_REQUESTS')
  def _executeInterceptOkTest(
      self,
      metric: MagicMock,
      *,
      requestMetadata: RequestMetadata,
      finalRequest: Any,
  ) -> None :
    """Test the counter gets incremented."""
    # Execute test.
    self.interceptor.khaleesiIntercept(request = finalRequest, **self.getInterceptParams())
    # Assert result.
    self._assertMetricCall(
      metric          = metric,
      requestMetadata = requestMetadata,
      status          = StatusCode.OK,
    )

  @patch('khaleesi.core.interceptors.server.prometheus.INCOMING_REQUESTS')
  def _executeInterceptKhaleesiExceptionTest(
      self,
      metric: MagicMock,
      *,
      requestMetadata: RequestMetadata,
      finalRequest: Any,
  ) -> None :
    """Test the counter gets incremented."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          metric.reset_mock()
          # Execute test.
          with self.assertRaises(KhaleesiException):
            self.interceptor.khaleesiIntercept(
              request = finalRequest,
              **self.getInterceptParams(
                executableMethod = khaleesiRaisingMethod(status = status, loglevel = loglevel),
              ),
            )
          # Assert result.
          self._assertMetricCall(
            metric          = metric,
            requestMetadata = requestMetadata,
            status          = status,
          )

  @patch('khaleesi.core.interceptors.server.prometheus.INCOMING_REQUESTS')
  def _executeInterceptOtherExceptionTest(
      self,
      metric: MagicMock,
      *,
      requestMetadata: RequestMetadata,
      finalRequest   : Any,
  ) -> None :
    """Test the counter gets incremented."""
    # Execute test.
    with self.assertRaises(Exception):
      self.interceptor.khaleesiIntercept(
        request = finalRequest,
        **self.getInterceptParams(executableMethod = exceptionRaisingMethod()),
      )
    # Assert result.
    self._assertMetricCall(
      metric          = metric,
      requestMetadata = requestMetadata,
      status          = StatusCode.UNKNOWN,
    )

  def _assertMetricCall(
      self, *,
      metric         : MagicMock,
      requestMetadata: RequestMetadata,
      status         : StatusCode,
  ) -> None :
    """Assert the metric call was correct."""
    metric.inc.assert_called_once()
    self.assertEqual(status         , metric.inc.call_args.kwargs['status'])
    self.assertEqual(requestMetadata, metric.inc.call_args.kwargs['peer'])
