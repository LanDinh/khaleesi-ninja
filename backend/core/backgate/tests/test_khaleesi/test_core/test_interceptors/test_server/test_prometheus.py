"""Test PrometheusServerInterceptor"""

# Python.
from typing import Any
from unittest.mock import MagicMock, patch

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


class PrometheusServerInterceptorTest(SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = PrometheusServerInterceptor()

  service_name = 'service-name'
  method_name  = 'method-name'

  @patch('khaleesi.core.interceptors.server.prometheus.OUTGOING_REQUESTS')
  def test_intercept_ok(self, metric: MagicMock) -> None :
    """Test the counter gets incremented."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label.lower()):
        # Prepare data.
        metric.reset_mock()
        request = self._get_request(user = user_type)
        # Execute test.
        self.interceptor.khaleesi_intercept(
          method       = lambda *args : None,
          request      = request,
          context      = MagicMock(),
          service_name = self.service_name,
          method_name  = self.method_name,
        )
        # Assert result.
        self.assert_metric_call(metric = metric, request = request, status = StatusCode.OK)

  @staticmethod
  def _get_request(*, user: int) -> Any :
    """Helper to create the request object."""
    request = MagicMock(request_metadata = RequestMetadata())
    request.request_metadata.user.type               = user
    request.request_metadata.caller.khaleesi_gate    = 'khaleesi-gate'
    request.request_metadata.caller.khaleesi_service = 'khaleesi-service'
    request.request_metadata.caller.grpc_service     = 'grpc-service'
    request.request_metadata.caller.grpc_method      = 'grpc-method'
    return request

  def assert_metric_call(self, *, metric: MagicMock, request: Any, status: StatusCode) -> None :
    """Assert the metric call was correct."""
    metric.inc.assert_called_once_with(
      status                = status,
      user                  = request.request_metadata.user.type,
      grpc_service          = self.service_name,
      grpc_method           = self.method_name,
      peer_khaleesi_gate    = request.request_metadata.caller.khaleesi_gate,
      peer_khaleesi_service = request.request_metadata.caller.khaleesi_service,
      peer_grpc_service     = request.request_metadata.caller.grpc_service,
      peer_grpc_method      = request.request_metadata.caller.grpc_method,
    )
