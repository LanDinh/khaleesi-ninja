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
    khaleesiGateName    = 'Gate'
    khaleesiServiceName = 'Khaleesi'
    grpcServiceName     = 'Service'
    grpcMethodName      = 'Method'
    def khaleesiIntercept(
        khaleesiGate   : str,
        khaleesiService: str,
        grpcService    : str,
        grpcMethod     : str,
        **_: Any,
    ) -> None :
      self.assertEqual(
        (khaleesiGateName, khaleesiServiceName, grpcServiceName, grpcMethodName),
        (khaleesiGate, khaleesiService, grpcService, grpcMethod),
      )
    self.interceptor.khaleesiIntercept = khaleesiIntercept
    # Execute test & assert result.
    self.interceptor.intercept(
      method              = lambda *args: None,
      request_or_iterator = MagicMock(),
      call_details        = MagicMock(method = f'/khaleesi.{khaleesiGateName}.{khaleesiServiceName}.{grpcServiceName}/{grpcMethodName}'),  # pylint: disable=line-too-long
    )
