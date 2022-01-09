"""Test server interceptor utility."""

# Python.
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.test_util import SimpleTestCase


class PrometheusServerInterceptorTest(SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = ServerInterceptor()

  def test_intercept(self) -> None :
    """Test the counter gets incremented."""
    # Prepare data.
    service_name = 'protobuf.package.Service'
    method_name = 'Method'
    full_interceptor_method_name = '/protobuf.package.Service/Method'
    self.interceptor.khaleesi_intercept = lambda **kwargs : self.assertEqual(  # type: ignore[assignment]  # pylint: disable=line-too-long
      (service_name, method_name),
      (kwargs['service_name'], kwargs['method_name'])
    )
    # Execute test and assert result.
    self.interceptor.intercept(
      method      = lambda *args: None,
      request     = MagicMock(),
      context     = MagicMock(),
      method_name = full_interceptor_method_name,
    )
