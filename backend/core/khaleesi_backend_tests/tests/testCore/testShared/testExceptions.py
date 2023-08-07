"""Test the exceptions."""

# Django.
from django.test import override_settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.testUtil.testCase import SimpleTestCase


class KhaleesiExceptionTestCase(SimpleTestCase):
  """Test the exceptions."""

  data = {
      'site'           : 'site',
      'app'            : 'app',
      'publicKey'      : 'public-key',
      'publicDetails'  : 'public-details',
      'privateMessage' : 'private-message',
      'privateDetails' : 'private-details',
  }

  @override_settings(DEBUG = True)
  def testFullDetailsInDebugMode(self) -> None :
    """Test that debug mode will provide full exception details."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          exception = KhaleesiException(status = status, loglevel = loglevel, **self.data)
          # Execute test.
          result = exception.toJson()
          # Assert result.
          self.assertIn('privateMessage', result)
          self.assertIn('privateDetails', result)
          self.assertIn('stacktrace'    , result)

  @override_settings(DEBUG = False)
  def testOnlyPublicDetailsInProductionMode(self) -> None :
    """Test that production mode will only provide public exception details."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          exception = KhaleesiException(status = status, loglevel = loglevel, **self.data)
          # Execute test.
          result = exception.toJson()
          # Assert result.
          self.assertNotIn('privateMessage', result)
          self.assertNotIn('privateDetails', result)
          self.assertNotIn('stacktrace'    , result)
