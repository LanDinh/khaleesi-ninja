"""Test server interceptor utility."""

# Python.
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.test_util.test_case import SimpleTestCase


class ServerInterceptorTest(SimpleTestCase):
  """Test server interceptor utility."""

  interceptor = ServerInterceptor()

  def test_intercept(self) -> None :
    """Test method interception."""
    # Prepare data.
    service = 'Service'
    method  = 'Method'
    khaleesi_intercept = lambda service_name, method_name, **kwargs : self.assertEqual(
      (service, method),
      (service_name, method_name),
    )
    self.interceptor.khaleesi_intercept = khaleesi_intercept  # type: ignore[assignment]
    # Execute test & assert result.
    self.interceptor.intercept(
      method      = lambda *args: None,
      request     = MagicMock(),
      context     = MagicMock(),
      method_name = f'/khaleesi.gate.service.{service}/{method}',
    )
