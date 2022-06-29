"""Test server interceptor utility."""

# Python.
from typing import Any
from unittest.mock import MagicMock, patch

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
    def khaleesi_intercept(service_name: str, method_name: str, **_: Any) -> None :
      self.assertEqual((service, method), (service_name, method_name))
    self.interceptor.khaleesi_intercept = khaleesi_intercept  # type: ignore[assignment]
    # Execute test & assert result.
    self.interceptor.intercept(
      method              = lambda *args: None,
      request_or_iterator = MagicMock(),
      context             = MagicMock(),
      method_name         = f'/khaleesi.gate.service.{service}/{method}',
    )

  @patch('khaleesi.core.interceptors.util.LOGGER')
  def test_skip_intercept(self, *_: MagicMock) -> None :
    """Test skipping of method interception."""
    for method in self.interceptor.skip_list:
      # Prepare data.
      khaleesi_intercept = MagicMock()
      self.interceptor.khaleesi_intercept = khaleesi_intercept  # type: ignore[assignment]
      # Execute test.
      self.interceptor.intercept(
        method              = lambda *args: None,
        request_or_iterator = MagicMock(),
        context             = MagicMock(),
        method_name         = method,
      )
      # Assert result.
      khaleesi_intercept.assert_not_called()
