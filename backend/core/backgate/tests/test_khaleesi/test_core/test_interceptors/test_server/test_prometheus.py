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
from khaleesi.core.test_util import SimpleTestCase
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
        expected_request = self._get_request(user = user_type, **request_params)
        # Execute test.
        self.interceptor.khaleesi_intercept(
          method       = lambda *args : None,
          request      = request if request is not None else expected_request,
          context      = MagicMock(),
          service_name = self.service_name,
          method_name  = self.method_name,
        )
        # Assert result.
        self.assert_metric_call(metric = metric, request = expected_request, status = StatusCode.OK)

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
        expected_request = self._get_request(user = user_type, **request_params)
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
            request      = request if request is not None else expected_request,
            context      = MagicMock(),
            service_name = self.service_name,
            method_name  = self.method_name,
          )
        # Assert result.
        self.assert_metric_call(metric = metric, request = expected_request, status = status)

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
        expected_request = self._get_request(user = user_type, **request_params)
        # Execute test.
        with self.assertRaises(Exception):
          self.interceptor.khaleesi_intercept(
            method       = lambda *args : _raise(Exception('exception')),
            request      = request if request is not None else expected_request,
            context      = MagicMock(),
            service_name = self.service_name,
            method_name  = self.method_name,
          )
        # Assert result.
        self.assert_metric_call(
          metric = metric,
          request = expected_request,
          status = StatusCode.UNKNOWN,
        )

  @staticmethod
  def _get_request(
      *,
      user: int,
      khaleesi_gate: Optional[str]    = 'khaleesi-gate',
      khaleesi_service: Optional[str] = 'khaleesi-service',
      grpc_service: Optional[str]     = 'grpc-service',
      grpc_method: Optional[str]      = 'grpc-method',
  ) -> Any :
    """Helper to create the request object."""
    request = MagicMock(request_metadata = RequestMetadata())
    request.request_metadata.user.type               = user
    request.request_metadata.caller.khaleesi_gate    = khaleesi_gate
    request.request_metadata.caller.khaleesi_service = khaleesi_service
    request.request_metadata.caller.grpc_service     = grpc_service
    request.request_metadata.caller.grpc_method      = grpc_method
    return request

  def assert_metric_call(self, *, metric: MagicMock, request: Any, status: StatusCode) -> None :
    """Assert the metric call was correct."""
    labels = {
        'user'                 : request.request_metadata.user.type,
        'grpc_service'         : self.service_name,
        'grpc_method'          : self.method_name,
        'peer_khaleesi_gate'   : request.request_metadata.caller.khaleesi_gate    or 'UNKNOWN',
        'peer_khaleesi_service': request.request_metadata.caller.khaleesi_service or 'UNKNOWN',
        'peer_grpc_service'    : request.request_metadata.caller.grpc_service     or 'UNKNOWN',
        'peer_grpc_method'     : request.request_metadata.caller.grpc_method      or 'UNKNOWN',
    }
    metric.inc.assert_called_once_with(status = status, **labels)
    metric.track_in_progress.assert_called_once_with(**labels)
