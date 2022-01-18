"""Test custom exceptions."""

# Django.
from django.test import override_settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.exceptions import KhaleesiException
from khaleesi.core.test_util.test_case import SimpleTestCase


class ExceptionTestCase(SimpleTestCase):
  """Test custom exceptions."""

  data = {
      'gate'           : 'gate',
      'service'        : 'service',
      'public_key'     : 'public-key',
      'public_details' : 'public-details',
      'private_details': 'private-details',
  }

  @override_settings(DEBUG = True)
  def test_full_details_in_debug_mode(self) -> None :
    """Test that debug mode will provide full exception details."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        exception = KhaleesiException(status = status, **self.data)
        # Execute test & assert result.
        self.assertEqual(self.data['private_details'], exception.public_details)
        self.assertEqual(self.data['private_details'], str(exception))

  @override_settings(DEBUG = False)
  def test_only_public_details_in_production_mode(self) -> None :
    """Test that production mode will only provide public exception details."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        exception = KhaleesiException(status = status, **self.data)
        # Execute test & assert result.
        self.assertEqual(self.data['public_details'], exception.public_details)
        self.assertEqual(self.data['public_details'], str(exception))
