"""Test LoggingServerInterceptor"""

# Python.
from typing import cast
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
    logger.debug.assert_called_once()
    logger.info.assert_called_once()
    self.assertEqual(request_metadata.caller, logging_request.upstream_request)
    self.assertEqual(-1               , logging_request.request_metadata.caller.request_id)
    self.assertEqual('core'           , logging_request.request_metadata.caller.khaleesi_gate)
    self.assertEqual('sawmill'        , logging_request.request_metadata.caller.khaleesi_service)
    self.assertEqual(self.service_name, logging_request.request_metadata.caller.grpc_service)
    self.assertEqual(self.method_name , logging_request.request_metadata.caller.grpc_method)
