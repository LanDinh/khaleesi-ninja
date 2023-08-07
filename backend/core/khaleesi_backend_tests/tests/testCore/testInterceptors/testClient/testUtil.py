"""Test client interceptor utility."""

# Python.
from typing import Any
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.interceptors.client.util import ClientInterceptor
from khaleesi.core.testUtil.testCase import SimpleTestCase


class ClientInterceptorTest(SimpleTestCase):
  """Test server interceptor utility."""

  interceptor = ClientInterceptor()

  def testIntercept(self) -> None :
    """Test method interception."""
    # Prepare data.
    siteName    = 'Site'
    appName     = 'Khaleesi'
    serviceName = 'Service'
    methodName  = 'Method'
    def khaleesiIntercept(
        site   : str,
        app    : str,
        service: str,
        method : str,
        **_: Any,
    ) -> None :
      self.assertEqual((siteName, appName, serviceName, methodName), (site, app, service, method))
    self.interceptor.khaleesiIntercept = khaleesiIntercept
    # Execute test & assert result.
    self.interceptor.intercept(
      method              = lambda *args: None,
      request_or_iterator = MagicMock(),
      call_details        = MagicMock(method = f'/khaleesi.{siteName}.{appName}.{serviceName}/{methodName}'),  # pylint: disable=line-too-long
    )
