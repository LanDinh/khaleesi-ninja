"""Test LoggingServerInterceptor"""

# Python.
from typing import Any, Dict, Optional, cast
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.logging import LoggingServerInterceptor
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
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
from khaleesi.proto.core_sawmill_pb2 import (
  Request as LoggingRequest,
  ResponseRequest as LoggingResponse,
  Error as LoggingError,
)


class LoggingServerInterceptorTestCase(ServerInterceptorTestMixin, SimpleTestCase):
  """Test LoggingServerInterceptor"""

  interceptor = LoggingServerInterceptor(channel_manager = MagicMock())

  def test_intercept_with_request_metadata(self) -> None :
    """Test intercept with metadata present."""
    self.interceptor.stub.LogRequest = MagicMock()
    self.interceptor.stub.LogResponse = MagicMock()
    for name, request_params in self.metadata_request_params:
      with self.subTest(case = name):
        self._execute_intercept_grpc_logging_test(  # pylint: disable=no-value-for-parameter
          request_params = request_params,
        )

  def test_intercept_without_request_metadata(self) -> None :
    """Test intercept with no metadata present."""
    self.interceptor.stub.LogRequest = MagicMock()
    self.interceptor.stub.LogResponse = MagicMock()
    self._execute_intercept_grpc_logging_test(  # pylint: disable=no-value-for-parameter
      request = {},
      request_params = self.empty_input,
    )

  @patch('khaleesi.core.interceptors.server.logging.LOGGER')
  def test_logging_khaleesi_exception(self, logger: MagicMock) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      for status in StatusCode:
        with self.subTest(user = user_label.lower(), status = status.name.lower()):
          # Prepare data.
          _, final_request = self.get_request(
            request = {},
            user = user_type,
            request_params = self.empty_input,
          )
          self.interceptor.stub.LogRequest.reset_mock()
          self.interceptor.stub.LogResponse.reset_mock()
          logger.reset_mock()
          context = MagicMock()
          STATE.reset()
          exception = default_khaleesi_exception(status = status)
          # Execute test.
          with self.assertRaises(KhaleesiException):
            self.interceptor.khaleesi_intercept(
              request = final_request,
              **self.get_intercept_params(
                context = context,
                method = khaleesi_raising_method(status = status),
              ),
            )
          # Assert result.
          self._assert_exception_logging_call(
            logger    = logger,
            context   = context,
            exception = exception,
          )

  @patch('khaleesi.core.interceptors.server.logging.LOGGER')
  def test_logging_other_exception(self, logger: MagicMock) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        _, final_request = self.get_request(
          request = {},
          user = user_type,
          request_params = self.empty_input,
        )
        self.interceptor.stub.LogRequest.reset_mock()
        self.interceptor.stub.LogResponse.reset_mock()
        logger.reset_mock()
        context = MagicMock()
        STATE.reset()
        exception = MaskingInternalServerException(exception = default_exception())
        # Execute test.
        with self.assertRaises(KhaleesiException):
          self.interceptor.khaleesi_intercept(
            request = final_request,
            **self.get_intercept_params(
              context = context,
              method = exception_raising_method(exception = exception),
            ),
          )
        # Assert result.
        self._assert_exception_logging_call(
          logger    = logger,
          context   = context,
          exception = exception,
        )

  @patch('khaleesi.core.interceptors.server.logging.LOGGER')
  def _execute_intercept_grpc_logging_test(
      self,
      logger: MagicMock,
      *,
      request: Optional[Any] = None,
      request_params: Dict[str, Any],
  ) -> None :
    """Execute the logging tests."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        request_metadata, final_request = self.get_request(
          request = request,
          user = user_type,
          **request_params,
        )
        self.interceptor.stub.LogRequest.reset_mock()
        self.interceptor.stub.LogResponse.reset_mock()
        logger.reset_mock()
        context = MagicMock()
        STATE.reset()
        # Execute test.
        self.interceptor.khaleesi_intercept(
          request = final_request,
          **self.get_intercept_params(context = context),
        )
        # Assert result.
        self._assert_logging_call(
          logger = logger,
          context = context,
          request_metadata = request_metadata,
        )

  def _assert_logging_call(
      self, *,
      logger          : MagicMock,
      context         : MagicMock,
      request_metadata: RequestMetadata,
  ) -> None :
    """Assert the logging calls were correct."""
    logging_request = cast(LoggingRequest, self.interceptor.stub.LogRequest.call_args.args[0])
    logging_response = cast(LoggingResponse, self.interceptor.stub.LogResponse.call_args.args[0])
    context.set_code.assert_not_called()
    context.set_details.assert_not_called()
    self.assertEqual(2, logger.info.call_count)
    self.assertEqual(request_metadata.caller, logging_request.upstream_request)
    self.assertEqual(-1                     , logging_request.request_metadata.caller.request_id)
    self.assertNotEqual(-1                  , logging_response.request_id)
    self.assertEqual('OK'                   , logging_response.response.status)

  def _assert_exception_logging_call(
      self, *,
      logger   : MagicMock,
      context  : MagicMock,
      exception: KhaleesiException,
  ) -> None :
    """Assert the logging calls were correct."""
    logging_response = cast(
      LoggingResponse,
      self.interceptor.stub.LogResponse.call_args.args[0],
    )
    logging_error = cast(
      LoggingError,
      self.interceptor.stub.LogError.call_args.args[0],
    )
    logger.error.assert_called_once()
    context.set_code.assert_called_once()
    context.set_details.assert_called_once()
    self.assertEqual(exception.status.name    , logging_response.response.status)
    self.assertEqual(exception.status.name    , logging_error.status)
    self.assertEqual(exception.gate           , logging_error.gate)
    self.assertEqual(exception.service        , logging_error.service)
    self.assertEqual(exception.public_key     , logging_error.public_key)
    self.assertEqual(exception.public_details , logging_error.public_details)
    self.assertEqual(exception.private_message, logging_error.private_message)
    self.assertEqual(exception.private_details, logging_error.private_details)
    self.assertIsNotNone(logging_error.stacktrace)
