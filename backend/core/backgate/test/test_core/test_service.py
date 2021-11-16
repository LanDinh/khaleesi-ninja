"""Test the core backgate service."""

# Django.
from django.test import TestCase

# khaleesi.ninja.
from core.service import SayHelloRequest, Service


class CoreBackgateServiceTestCase(TestCase):
  """Test the core backgate service."""

  def setUp(self) -> None :
    """Instantiate the service."""
    self.service =  Service()

  def test_say_hello(self) -> None :
    """Test saying hello."""
    # Prepare data.
    name = 'Khaleesi, Mother of Dragons, Breaker of Chains'
    request = SayHelloRequest(name = name)
    # Execute test.
    response = self.service.SayHello(request = request, context = None)
    # Assert results.
    self.assertIn(name, response.message)
