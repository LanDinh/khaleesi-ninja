"""Test LoggingServerInterceptor"""

# Python.
from typing import cast, Any
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

  @patch('khaleesi.core.interceptors.server.logging.LOGGER')
  def test_db_logging(self, logger: MagicMock) -> None :
    """Test db logging."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        request_metadata, final_request = self.get_request(
          request = None,
          user = user_type,
          **self.empty_input,
        )
        logger.reset_mock()
        db_module = MagicMock()
        # Execute test.
        with patch.dict('sys.modules', { 'microservice.models': db_module }):
          self.interceptor.khaleesi_intercept(
            request = final_request,
            **self.get_intercept_params(),
          )
        # Assert result.
        self._assert_logging_call(
          logging_stub= db_module,
          logger = logger,
          request_metadata = request_metadata,
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
        logger.reset_mock()
        db_module = MagicMock()

        # noinspection PyUnusedLocal
        def method(*args: Any, **kwargs: Any) -> None :
          raise KhaleesiException(
            status = StatusCode.INTERNAL,
            gate = '',
            service = '',
            public_key = '',
            public_details = '',
            private_details = '',
          )
        # Execute test.
        with patch.dict('sys.modules', { 'microservice.models': db_module }):
          with self.assertRaises(KhaleesiException):
            self.interceptor.khaleesi_intercept(
              request = final_request,
              **self.get_intercept_params(method = method),
            )
        # Assert result.
        logging_response = cast(
          LoggingResponse,
          db_module.Request.objects.log_response.call_args.kwargs['grpc_response'],
        )
        logger.error.assert_called_once()
        self.assertEqual('INTERNAL', logging_response.response.status)

  def _assert_logging_call(
      self, *,
      logging_stub: MagicMock,
      logger: MagicMock,
      request_metadata: RequestMetadata,
  ) -> None :
    """Assert the metric call was correct."""
    logging_request = cast(
      LoggingRequest,
      logging_stub.Request.objects.log_request.call_args.kwargs['grpc_request'],
    )
    logging_response = cast(
      LoggingResponse,
      logging_stub.Request.objects.log_response.call_args.kwargs['grpc_response'],
    )
    logger.debug.assert_called_once()
    self.assertEqual(2, logger.info.call_count)
    self.assertEqual(request_metadata.caller, logging_request.upstream_request)
    self.assertEqual(-1               , logging_request.request_metadata.caller.request_id)
    self.assertEqual('core'           , logging_request.request_metadata.caller.khaleesi_gate)
    self.assertEqual('sawmill'        , logging_request.request_metadata.caller.khaleesi_service)
    self.assertEqual(self.service_name, logging_request.request_metadata.caller.grpc_service)
    self.assertEqual(self.method_name , logging_request.request_metadata.caller.grpc_method)
    self.assertEqual('OK'             , logging_response.response.status)
