"""Test LoggingServerInterceptor"""

# Python.
from typing import Any, Dict, Optional, cast
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.logging import LoggingServerInterceptor
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.logging.text_logger import LogLevel
from khaleesi.core.shared.state import STATE
from khaleesi.core.test_util.exceptions import (
  khaleesi_raising_method,
  default_khaleesi_exception,
  exception_raising_method,
  default_exception,
)
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


@patch('khaleesi.core.interceptors.server.logging.SINGLETON')
class LoggingServerInterceptorTestCase(ServerInterceptorTestMixin, SimpleTestCase):
  """Test LoggingServerInterceptor"""

  interceptor = LoggingServerInterceptor()

  def test_intercept_with_request_metadata(self, singleton: MagicMock) -> None :
    """Test intercept with metadata present."""
    for name, request_params in self.metadata_request_params:
      with self.subTest(case = name):
        self._execute_intercept_grpc_logging_test(  # pylint: disable=no-value-for-parameter
          request_params = request_params,
          singleton      = singleton,
        )

  def test_intercept_without_request_metadata(self, singleton: MagicMock) -> None :
    """Test intercept with no metadata present."""
    self._execute_intercept_grpc_logging_test(  # pylint: disable=no-value-for-parameter
      request        = {},
      request_params = self.empty_input,
      singleton      = singleton,
    )

  def test_logging_khaleesi_exception(self, singleton: MagicMock) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      for status in StatusCode:
        for loglevel in LogLevel:
          with self.subTest(user = user_label, status = status.name, loglevel = loglevel.name):
            # Prepare data.
            _, final_request = self.get_request(
              request = {},
              user = user_type,
              request_params = self.empty_input,
            )
            STATE.reset()
            exception = default_khaleesi_exception(status = status, loglevel = loglevel)
            # Execute test.
            with self.assertRaises(KhaleesiException):
              self.interceptor.khaleesi_intercept(
                request = final_request,
                **self.get_intercept_params(
                  method = khaleesi_raising_method(status = status, loglevel = loglevel),
                ),
              )
            # Assert result.
            self._assert_exception_logging_call(
              loglevel  = loglevel,
              exception = exception,
              singleton = singleton,
            )

  def test_logging_other_exception(self, singleton: MagicMock) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        _, final_request = self.get_request(
          request = {},
          user = user_type,
          request_params = self.empty_input,
        )
        STATE.reset()
        exception = MaskingInternalServerException(exception = default_exception())
        # Execute test.
        with self.assertRaises(KhaleesiException):
          self.interceptor.khaleesi_intercept(
            request = final_request,
            **self.get_intercept_params(method = exception_raising_method(exception = exception)),
          )
        # Assert result.
        self._assert_exception_logging_call(
          loglevel  = LogLevel.FATAL,
          exception = exception,
          singleton = singleton,
        )

  def _execute_intercept_grpc_logging_test(
      self, *,
      request       : Optional[Any] = None,
      request_params: Dict[str, Any],
      singleton     : MagicMock,
  ) -> None :
    """Execute the logging tests."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        request_metadata, final_request = self.get_request(
          request = request,
          user    = user_type,
          **request_params,
        )
        context = MagicMock()
        STATE.reset()
        # Execute test.
        self.interceptor.khaleesi_intercept(
          request = final_request,
          **self.get_intercept_params(context = context),
        )
        # Assert result.
        self._assert_logging_call(
          context          = context,
          request_metadata = request_metadata,
          singleton        = singleton
        )

  def _assert_logging_call(
      self, *,
      context         : MagicMock,
      request_metadata: RequestMetadata,
      singleton       : MagicMock,
  ) -> None :
    """Assert the logging calls were correct."""
    upstream_request = cast(
      RequestMetadata,
      singleton.structured_logger.log_request.call_args.kwargs['upstream_request'],
    )
    status = cast(
      StatusCode,
      singleton.structured_logger.log_response.call_args.kwargs['status'],
    )
    context.set_code.assert_not_called()
    context.set_details.assert_not_called()
    self.assertEqual(request_metadata.caller, upstream_request.caller)
    self.assertEqual(StatusCode.OK          , status)

  def _assert_exception_logging_call(
      self, *,
      exception: KhaleesiException,
      loglevel : LogLevel,
      singleton: MagicMock,
  ) -> None :
    """Assert the logging calls were correct."""
    status = cast(
      StatusCode,
      singleton.structured_logger.log_response.call_args.kwargs['status'],
    )
    logged_exception = cast(
      KhaleesiException,
      singleton.structured_logger.log_error.call_args.kwargs['exception'],
    )
    self.assertEqual(exception.status         , status)
    self.assertEqual(exception.status         , logged_exception.status)
    self.assertEqual(exception.loglevel       , loglevel)
    self.assertEqual(exception.loglevel       , logged_exception.loglevel)
    self.assertEqual(exception.gate           , logged_exception.gate)
    self.assertEqual(exception.service        , logged_exception.service)
    self.assertEqual(exception.public_key     , logged_exception.public_key)
    self.assertEqual(exception.public_details , logged_exception.public_details)
    self.assertEqual(exception.private_message, logged_exception.private_message)
    self.assertEqual(exception.private_details, logged_exception.private_details)
    self.assertIsNotNone(logged_exception.stacktrace)
