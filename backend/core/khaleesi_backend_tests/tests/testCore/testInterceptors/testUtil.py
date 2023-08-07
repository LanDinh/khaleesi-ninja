"""Test interceptor utility."""

# khaleesi.ninja.
from khaleesi.core.interceptors.util import Interceptor
from khaleesi.core.testUtil.testCase import SimpleTestCase


class InterceptorTest(SimpleTestCase):
  """Test interceptor utility"""

  interceptor = Interceptor()

  def testProcessMethodName(self) -> None :
    """Test the method name gets processed correctly."""
    for description, iSite, iApp, iService, iMethod, raw in [
        ( 'full' , 'site', 'app', 'Service', 'Method', '/khaleesi.site.app.Service/Method' ),
        ( 'no service', 'site', 'app', 'UNKNOWN', 'Method', '/khaleesi.site.app/Method' ),
        ( 'no app', 'site', 'UNKNOWN', 'UNKNOWN', 'Method', '/khaleesi.site/Method' ),
        ( 'no site', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Method', '/khaleesi/Method' ),
        ( 'no method', 'site', 'app', 'Service', 'UNKNOWN', '/khaleesi.site.app.Service/' ),
        ( 'empty input', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', '' ),
    ]:
      with self.subTest(case = description):
        # Execute test.
        oSite, oApp, oService, oMethod = self.interceptor.processMethodName(raw = raw)
        # Assert result.
        self.assertEqual(iSite   , oSite)
        self.assertEqual(iApp    , oApp)
        self.assertEqual(iService, oService)
        self.assertEqual(iMethod , oMethod)

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
