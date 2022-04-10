"""Test LoggingServerInterceptor"""

# Python.
from typing import Any, Dict, Optional, cast
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.interceptors.server.logging import LoggingServerInterceptor
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import Request as LoggingRequest


class LoggingServerInterceptorTestCase(ServerInterceptorTestMixin, SimpleTestCase):
  """Test LoggingServerInterceptor"""

  interceptor = LoggingServerInterceptor(channel_manager = MagicMock())

  def test_intercept_with_request_metadata(self) -> None :
    """Test intercept with metadata present."""
    for name, request_params in self.metadata_request_params:
      with self.subTest(case = name):
        self._execute_intercept_execute_intercept_grpc_logging_test(  # pylint: disable=no-value-for-parameter
          request_params = request_params,
        )

  def test_intercept_without_request_metadata(self) -> None :
    """Test intercept with no metadata present."""
    self._execute_intercept_execute_intercept_grpc_logging_test(  # pylint: disable=no-value-for-parameter
      request = {},
      request_params = self.empty_input,
    )

  @patch('khaleesi.core.interceptors.server.logging.LOGGER')
  @patch('khaleesi.core.interceptors.server.logging.LumberjackStub')
  def _execute_intercept_execute_intercept_grpc_logging_test(
      self,
      logging_stub: MagicMock,
      logger: MagicMock,
      *,
      request: Optional[Any] = None,
      request_params: Dict[str, Any],
  ) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        request_metadata, final_request = self.get_request(
          request = request,
          user = user_type,
          **request_params,
        )
        logging_stub.reset_mock()
        logger.reset_mock()
        # Execute test.
        self.interceptor.khaleesi_intercept(request = final_request, **self.get_intercept_params())
        # Assert result.
        self._assert_logging_call(
          logging_stub = logging_stub,
          logger = logger,
          request_metadata = request_metadata,
        )

  def _assert_logging_call(
      self, *,
      logging_stub: MagicMock,
      logger: MagicMock,
      request_metadata: RequestMetadata,
  ) -> None :
    """Assert the metric call was correct."""
    logging_request = cast(LoggingRequest, logging_stub.return_value.LogRequest.call_args.args[0])
    logger.debug.assert_called_once()
    logger.info.assert_called_once()
    self.assertEqual(request_metadata.caller, logging_request.upstream_request)
    self.assertEqual(-1               , logging_request.request_metadata.caller.request_id)
    self.assertEqual('core'           , logging_request.request_metadata.caller.khaleesi_gate)
    self.assertEqual('backgate'       , logging_request.request_metadata.caller.khaleesi_service)
    self.assertEqual(self.service_name, logging_request.request_metadata.caller.grpc_service)
    self.assertEqual(self.method_name , logging_request.request_metadata.caller.grpc_method)
