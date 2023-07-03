"""Test server interceptor utility."""

# Python.
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import GrpcRequest


class ServerInterceptorTest(SimpleTestCase):
  """Test server interceptor utility."""

  interceptor = ServerInterceptor()

  def testIntercept(self) -> None :
    """Test method interception."""
    # Prepare data.
    service = 'Service'
    method  = 'Method'
    khaleesiIntercept = MagicMock()
    self.interceptor.khaleesiIntercept = khaleesiIntercept  # type: ignore[assignment]
    # Execute test.
    self.interceptor.intercept(
      method              = lambda *args: None,
      request_or_iterator = MagicMock(),
      context             = MagicMock(),
      method_name         = f'/khaleesi.gate.service.{service}/{method}',
    )
    # Assert result.
    khaleesiIntercept.assert_called_once()

  def testSkipIntercept(self) -> None :
    """Test skipping of method interception."""
    for method in self.interceptor.skipList:
      # Prepare data.
      khaleesiIntercept = MagicMock()
      self.interceptor.khaleesiIntercept = khaleesiIntercept  # type: ignore[assignment]
      # Execute test.
      self.interceptor.intercept(
        method              = lambda *args: None,
        request_or_iterator = MagicMock(),
        context             = MagicMock(),
        method_name         = method,
      )
      # Assert result.
      khaleesiIntercept.assert_not_called()

  def testGetUpstreamRequest(self) -> None :
    """Test if we can fetch the upstream request."""
    # Prepare data.
    request = GrpcRequest()
    request.requestMetadata.grpcCaller.requestId = 'request-id'
    # Execute test.
    result = self.interceptor.getUpstreamRequest(request = request)
    # Assert result.
    self.assertEqual(request.requestMetadata.grpcCaller.requestId, result.grpcCaller.requestId)



  def testGetUpstreamRequestFallback(self) -> None :
    """Test if we can fetch the upstream request."""
    # Execute test.
    result = self.interceptor.getUpstreamRequest(request = object())
    # Assert result.
    self.assertEqual('', result.grpcCaller.requestId)
