"""Test the custom request state interceptor."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE
from khaleesi.core.test_util.interceptor import ServerInterceptorTestMixin
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from microservice.request_state_interceptor import BackgateRequestStateServerInterceptor


class RequestStateServerInterceptorTest(ServerInterceptorTestMixin, SimpleTestCase):
  """Test RequestStateServerInterceptor."""

  interceptor = BackgateRequestStateServerInterceptor()

  @patch('microservice.request_state_interceptor.SINGLETON')
  def test_set_backgate_request_id_with_request_metadata(self, singleton: MagicMock) -> None :
    """Test setting the backgate request id."""
    for name, request_params in self.metadata_request_params:
      for user_label, user_type in User.UserType.items():
        with self.subTest(case = name, user = user_label):
          # Prepare data.
          request_metadata, _ = self.get_request(
            request = None,
            user = user_type,
            **request_params,
          )
          STATE.reset()
          singleton.reset_mock()
          # Execute test.
          self.interceptor.set_backgate_request_id(upstream = request_metadata)
          # Assert result.
          self.assertNotEqual(
            request_metadata.caller.backgate_request_id,
            STATE.request.backgate_request_id,
          )
          singleton.structured_logger.log_backgate_request.assert_called_once_with()
