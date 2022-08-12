"""Test the exceptions."""

# Django.
from django.test import override_settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.test_util.test_case import SimpleTestCase


class KhaleesiExceptionTestCase(SimpleTestCase):
  """Test the exceptions."""

  data = {
      'gate'            : 'gate',
      'service'         : 'service',
      'public_key'      : 'public-key',
      'public_details'  : 'public-details',
      'private_message' : 'private-message',
      'private_details' : 'private-details',
  }

  @override_settings(DEBUG = True)
  def test_full_details_in_debug_mode(self) -> None :
    """Test that debug mode will provide full exception details."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        exception = KhaleesiException(status = status, **self.data)
        # Execute test.
        result = exception.to_json()
        # Assert result.
        self.assertIn('private_message', result)
        self.assertIn('private_details', result)
        self.assertIn('stacktrace', result)

  @override_settings(DEBUG = False)
  def test_only_public_details_in_production_mode(self) -> None :
    """Test that production mode will only provide public exception details."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        exception = KhaleesiException(status = status, **self.data)
        # Execute test.
        result = exception.to_json()
        # Assert result.
        self.assertNotIn('private_message', result)
        self.assertNotIn('private_details', result)
        self.assertNotIn('stacktrace', result)
