"""Test RequestStateServerInterceptor."""

# Python.
from functools import partial
from typing import Optional, Any, Dict
from unittest.mock import MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.request_state import RequestStateServerInterceptor
from khaleesi.core.shared.logger import LogLevel
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.core.test_util.exceptions import khaleesi_raising_method
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User


class RequestStateServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test RequestStateServerInterceptor."""

  interceptor = RequestStateServerInterceptor(structured_logger = MagicMock())

  def test_intercept_with_request_metadata(self) -> None :
    """Test intercept with metadata present."""
    for name, request_params in self.metadata_request_params:
      for user_label, user_type in User.UserType.items():
        with self.subTest(case = name, user = user_label):
          self._execute_intercept_tests(request_params = request_params, user_type = user_type)

  def test_intercept_without_request_metadata(self) -> None :
    """Test intercept with no metadata present."""
    self._execute_intercept_tests(
      request = {},
      request_params = self.empty_input,
      user_type = User.UserType.UNKNOWN,
    )

  def _execute_intercept_tests(
      self, *,
      request: Optional[Any] = None,
      request_params: Dict[str, Any],
      user_type: int,
  ) -> None :
    """Execute all typical intercept tests."""
    for test in [
        self._execute_intercept_ok_test,
        self._execute_intercept_khaleesi_exception_test,
        self._execute_intercept_other_exception_test,
    ]:
      with self.subTest(test = test.__name__):
        _, final_request = self.get_request(
          request = request,
          user = user_type,  # type: ignore[arg-type]
          **request_params,
        )
        test(final_request = final_request, user_type = user_type)  # pylint: disable=no-value-for-parameter

  def _execute_intercept_ok_test(self, *, final_request: Any, user_type: int) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    def _method(*_: Any) -> None :
      self._assert_not_clean_state(user_type = user_type)
    # Execute test.
    self.interceptor.khaleesi_intercept(
      request = final_request,
      **self.get_intercept_params(method = _method),
    )
    # Assert result.
    self._assert_clean_state()

  def _execute_intercept_khaleesi_exception_test(
      self, *,
      final_request: Any,
      user_type: int,
  ) -> None :
    """Test the counter gets incremented."""
    context = MagicMock()
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          context.reset_mock()
          # Execute test.
          self.interceptor.khaleesi_intercept(
            request = final_request,
            **self.get_intercept_params(
              context = context,
              method  = khaleesi_raising_method(
                method   = partial(self._assert_not_clean_state, user_type = user_type),
                status   = status,
                loglevel = loglevel,
              ),
            ),
          )
          # Assert result.
          self._assert_clean_state()
          context.abort.assert_called_once()

  def _execute_intercept_other_exception_test(self, *, final_request: Any, user_type: int) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    context = MagicMock()
    def _method(*_: Any) -> None :
      self._assert_not_clean_state(user_type = user_type)
      raise Exception('exception')
    # Execute test.
    self.interceptor.khaleesi_intercept(
      request = final_request,
      **self.get_intercept_params(context = context, method = _method),
    )
    # Assert result.
    self._assert_clean_state()
    context.abort.assert_called_once()

  def _assert_clean_state(self) -> None :
    """Assert a clean state."""
    self.assertEqual('UNKNOWN'       , STATE.request.grpc_service)
    self.assertEqual('UNKNOWN'       , STATE.request.grpc_method)
    self.assertEqual('UNKNOWN'       , STATE.user.user_id)
    self.assertEqual(UserType.UNKNOWN, STATE.user.type)

  # noinspection PyUnusedLocal
  def _assert_not_clean_state(self, *args: Any, user_type: int, **kwargs: Any) -> None :
    """Assert a clean state."""
    self.assertNotEqual('UNKNOWN'       , STATE.request.grpc_service)
    self.assertNotEqual('UNKNOWN'       , STATE.request.grpc_method)
    self.assertNotEqual('UNKNOWN'       , STATE.user.user_id)
    self.assertEqual(UserType(user_type), STATE.user.type)
