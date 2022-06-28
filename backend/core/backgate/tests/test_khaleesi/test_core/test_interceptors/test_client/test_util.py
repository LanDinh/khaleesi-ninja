"""Test client interceptor utility."""

# Python.
from typing import Any
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.interceptors.client.util import ClientInterceptor
from khaleesi.core.test_util.test_case import SimpleTestCase


class ClientInterceptorTest(SimpleTestCase):
  """Test server interceptor utility."""

  interceptor = ClientInterceptor()

  def test_intercept(self) -> None :
    """Test method interception."""
    # Prepare data.
    khaleesi_gate_name = 'Gate'
    khaleesi_service_name = 'Khaleesi'
    grpc_service_name = 'Service'
    grpc_method_name  = 'Method'
    def khaleesi_intercept(
        khaleesi_gate: str,
        khaleesi_service: str,
        grpc_service: str,
        grpc_method: str,
        **_: Any,
    ) -> None :
      self.assertEqual(
        (khaleesi_gate_name, khaleesi_service_name, grpc_service_name, grpc_method_name),
        (khaleesi_gate, khaleesi_service, grpc_service, grpc_method),
      )
    self.interceptor.khaleesi_intercept = khaleesi_intercept  # type: ignore[assignment]
    # Execute test & assert result.
    self.interceptor.intercept(
      method              = lambda *args: None,
      request_or_iterator = MagicMock(),
      call_details        = MagicMock(method = f'/khaleesi.{khaleesi_gate_name}.{khaleesi_service_name}.{grpc_service_name}/{grpc_method_name}'),  # pylint: disable=line-too-long
    )
