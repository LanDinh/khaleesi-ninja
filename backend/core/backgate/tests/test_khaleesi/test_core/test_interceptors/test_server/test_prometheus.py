"""Test PrometheusServerInterceptor"""

# Python.
from functools import partial
from itertools import product
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.exceptions import KhaleesiException
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


def _raise(exception: Exception) -> None :
  """Helper to raise exceptions in lambdas."""
  raise exception


class PrometheusServerInterceptorTest(SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = PrometheusServerInterceptor()

  service_name = 'service-name'
  method_name  = 'method-name'

  def test_intercept_with_request_metadata(self) -> None :
    """Test intercept with metadata present."""
    for name, request_params in [
        ( 'full input'            , {} ),
        ( 'empty khaleesi_gate'   , { 'khaleesi_gate'   : '' } ),
        ( 'empty khaleesi_service', { 'khaleesi_service': '' } ),
        ( 'empty grpc_service'    , { 'grpc_service'    : '' } ),
        ( 'empty grpc_method'     , { 'grpc_method'     : '' } ),
        ( 'empty input', {
            'khaleesi_gate'   : '',
            'khaleesi_service': '',
            'grpc_service'    : '',
            'grpc_method'     : '',
        })
    ]:
      with self.subTest(case = name):
        self._execute_intercept_tests(request_params = request_params)  # type: ignore[arg-type]

  def test_intercept_without_request_metadata(self) -> None :
    """Test intercept with no metadata present."""
    self._execute_intercept_tests(request = {}, request_params = {
        'khaleesi_gate'   : '',
        'khaleesi_service': '',
        'grpc_service'    : '',
        'grpc_method'     : '',
    })

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
      with self.subTest(test = test.__name__):
        test(request = request, request_params = request_params)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.core.interceptors.server.prometheus.INCOMING_REQUESTS')
  def _execute_intercept_ok_test(
      self,
      metric: MagicMock,
      *,
      request: Optional[Any] = None,
      request_params: Dict[str, Any],
  ) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        metric.reset_mock()
        if request is None:
          request_metadata = self._get_request(user = user_type, **request_params)
          final_request = MagicMock(request_metadata = request_metadata)
        else:
          request_metadata = RequestMetadata()
          final_request = request
        # Execute test.
        self.interceptor.khaleesi_intercept(
          method       = lambda *args : None,
          request      = final_request,
          context      = MagicMock(),
          service_name = self.service_name,
          method_name  = self.method_name,
        )
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
      request: Optional[Any] = None,
      request_params: Dict[str, Any],
  ) -> None :
    """Test the counter gets incremented."""
    for status, (user_label, user_type) in product(StatusCode, User.UserType.items()):
      with self.subTest(status = status.name, user = user_label.lower()):
        # Prepare data.
        metric.reset_mock()
        if request is None:
          request_metadata = self._get_request(user = user_type, **request_params)
          final_request = MagicMock(request_metadata = request_metadata)
        else:
          request_metadata = RequestMetadata()
          final_request = request
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
          self.interceptor.khaleesi_intercept(
            method       = partial(
              lambda inner_exception, *args : _raise(inner_exception),
              exception,
            ),
            request      = final_request,
            context      = MagicMock(),
            service_name = self.service_name,
            method_name  = self.method_name,
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
      request: Optional[Any] = None,
      request_params: Dict[str, Any],
  ) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        metric.reset_mock()
        if request is None:
          request_metadata = self._get_request(user = user_type, **request_params)
          final_request = MagicMock(request_metadata = request_metadata)
        else:
          request_metadata = RequestMetadata()
          final_request = request
        # Execute test.
        with self.assertRaises(Exception):
          self.interceptor.khaleesi_intercept(
            method       = lambda *args : _raise(Exception('exception')),
            request      = final_request,
            context      = MagicMock(),
            service_name = self.service_name,
            method_name  = self.method_name,
          )
        # Assert result.
        self._assert_metric_call(
          metric           = metric,
          request_metadata = request_metadata,
          status           = StatusCode.UNKNOWN,
        )

  @staticmethod
  def _get_request(
      *,
      user            : 'User.UserType.V' = User.UserType.UNKNOWN,
      khaleesi_gate   : str               = 'khaleesi-gate',
      khaleesi_service: str               = 'khaleesi-service',
      grpc_service    : str               = 'grpc-service',
      grpc_method     : str               = 'grpc-method',
  ) -> RequestMetadata :
    """Helper to create the request object."""
    request_metadata = RequestMetadata()
    request_metadata.user.type = user
    request_metadata.caller.khaleesi_gate    = khaleesi_gate
    request_metadata.caller.khaleesi_service = khaleesi_service
    request_metadata.caller.grpc_service     = grpc_service
    request_metadata.caller.grpc_method      = grpc_method
    return request_metadata

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
