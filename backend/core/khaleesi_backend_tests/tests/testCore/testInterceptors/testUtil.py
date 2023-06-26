"""Test interceptor utility."""

# khaleesi.ninja.
from khaleesi.core.interceptors.util import Interceptor
from khaleesi.core.testUtil.testCase import SimpleTestCase


class InterceptorTest(SimpleTestCase):
  """Test interceptor utility"""

  interceptor = Interceptor()

  def testProcessMethodName(self) -> None :
    """Test the method name gets processed correctly."""
    for description, iGate, iService, iGrpcService, iGrpcMethod, raw in [
        ( 'full', 'gate', 'service', 'GrpcService', 'Method', '/khaleesi.gate.service.GrpcService/Method' ),  # pylint: disable=line-too-long
        ( 'no g service', 'gate', 'service', 'UNKNOWN', 'Method', '/khaleesi.gate.service/Method' ),
        ( 'no k service', 'gate', 'UNKNOWN', 'UNKNOWN', 'Method', '/khaleesi.gate/Method' ),
        ( 'no service', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Method', '/khaleesi/Method' ),
        ( 'no method', 'gate', 'service', 'GrpcService', 'UNKNOWN', '/khaleesi.gate.service.GrpcService/' ),  # pylint: disable=line-too-long
        ( 'empty input', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', '' ),
    ]:
      with self.subTest(case = description):
        # Execute test.
        oGate, oService, oGrpcService, oGrpcMethod = self.interceptor.processMethodName(
          raw = raw,
        )
        # Assert result.
        self.assertEqual(iGate       , oGate)
        self.assertEqual(iService    , oService)
        self.assertEqual(iGrpcService, oGrpcService)
        self.assertEqual(iGrpcMethod , oGrpcMethod)

  def testSkipInterceptors(self) -> None :
    """Test skipping of interceptors."""
    for method in self.interceptor.skipList:
      # Prepare data & execute test.
      result = self.interceptor.skipInterceptors(raw = method)
      # Assert result.
      self.assertTrue(result)

  def testDontSkipInterceptors(self) -> None :
    """Test skipping of interceptors."""
    # Prepare data & execute test.
    result = self.interceptor.skipInterceptors(raw = 'some.test.Service/Method')
    # Assert result.
    self.assertFalse(result)
