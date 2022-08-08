"""Test LoggingServerInterceptor"""

# Python.
from typing import Any, Dict, Optional, cast
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.logging import LoggingServerInterceptor
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import (
  Request as LoggingRequest,
  ResponseRequest as LoggingResponse,
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
  def test_logging_non_ok_status(self, logger: MagicMock) -> None :
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

        # noinspection PyUnusedLocal
        def method(*args: Any, **kwargs: Any) -> None :
          raise KhaleesiException(
            status          = StatusCode.INTERNAL,
            gate            = '',
            service         = '',
            public_key      = '',
            public_details  = '',
            private_message = '',
            private_details = '',
          )
        # Execute test.
        with self.assertRaises(KhaleesiException):
          self.interceptor.khaleesi_intercept(
            request = final_request,
            **self.get_intercept_params(method = method),
          )
        # Assert result.
        logging_response = cast(
          LoggingResponse,
          self.interceptor.stub.LogResponse.call_args.args[0],
        )
        logger.error.assert_called_once()
        self.assertEqual('INTERNAL', logging_response.response.status)

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
        # Execute test.
        self.interceptor.khaleesi_intercept(request = final_request, **self.get_intercept_params())
        # Assert result.
        self._assert_logging_call(
          logger = logger,
          request_metadata = request_metadata,
        )

  def _assert_logging_call(
      self, *,
      logger: MagicMock,
      request_metadata: RequestMetadata,
  ) -> None :
    """Assert the logging calls were correct."""
    logging_request = cast(LoggingRequest, self.interceptor.stub.LogRequest.call_args.args[0])
    logging_response = cast(LoggingResponse, self.interceptor.stub.LogResponse.call_args.args[0])
    logger.debug.assert_called_once()
    self.assertEqual(2, logger.info.call_count)
    self.assertEqual(request_metadata.caller, logging_request.upstream_request)
    self.assertEqual(-1               , logging_request.request_metadata.caller.request_id)
    self.assertEqual('core'           , logging_request.request_metadata.caller.khaleesi_gate)
    self.assertEqual('backgate'       , logging_request.request_metadata.caller.khaleesi_service)
    self.assertEqual(self.service_name, logging_request.request_metadata.caller.grpc_service)
    self.assertEqual(self.method_name , logging_request.request_metadata.caller.grpc_method)
    self.assertEqual('OK'             , logging_response.response.status)
