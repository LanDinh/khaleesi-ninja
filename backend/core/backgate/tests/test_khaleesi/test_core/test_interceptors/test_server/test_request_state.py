"""Test RequestStateServerInterceptor."""

# Python.
from functools import partial
from typing import Optional, Any, Dict

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.request_state import RequestStateServerInterceptor
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.shared.state import STATE
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User


def _raise(exception: Exception) -> None :
  """Helper to raise exceptions in lambdas."""
  raise exception


class RequestStateServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test RequestStateServerInterceptor."""

  interceptor = RequestStateServerInterceptor()

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
          _, final_request = self.get_request(
            request = request,
            user = user_type,
            **request_params,
          )
          test(final_request = final_request)  # pylint: disable=no-value-for-parameter

  def _execute_intercept_ok_test(self, *, final_request: Any) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    def _method(*_: Any) -> None :
      self.assertNotEqual('UNKNOWN', STATE.request.service_name)
      self.assertNotEqual('UNKNOWN', STATE.request.method_name)
    # Execute test & assert result.
    self.interceptor.khaleesi_intercept(
      request = final_request,
      **self.get_intercept_params(method = _method),
    )

  def _execute_intercept_khaleesi_exception_test(self, *, final_request: Any) -> None :
    """Test the counter gets incremented."""
    def _method(*_: Any, exception: Exception) -> None :
      self.assertNotEqual('UNKNOWN', STATE.request.service_name)
      self.assertNotEqual('UNKNOWN', STATE.request.method_name)
      raise exception
    for status in StatusCode:
      with self.subTest(status = status.name):
        # Prepare data.
        current_exception = KhaleesiException(
          status          = status,
          gate            = 'gate',
          service         = 'service',
          public_key      = 'public-key',
          public_details  = 'public-details',
          private_message = 'private-message',
          private_details = 'private-details',
        )
        # Execute test & assert result.
        with self.assertRaises(KhaleesiException):
          self.interceptor.khaleesi_intercept(
            request = final_request,
            **self.get_intercept_params(
              method = partial(
                lambda inner_exception, *args : _method(*args, exception = inner_exception),
                current_exception),
            ),
          )

  def _execute_intercept_other_exception_test(self, *, final_request: Any) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    def _method(*_: Any) -> None :
      self.assertNotEqual('UNKNOWN', STATE.request.service_name)
      self.assertNotEqual('UNKNOWN', STATE.request.method_name)
      raise Exception('exception')
    # Execute test & assert result.
    with self.assertRaises(Exception):
      self.interceptor.khaleesi_intercept(
        request = final_request,
        **self.get_intercept_params(method = _method),
      )

  def _assert_clean_state(self) -> None :
    """Assert a clean state."""
    self.assertEqual('UNKNOWN', STATE.request.service_name)
    self.assertEqual('UNKNOWN', STATE.request.method_name)
