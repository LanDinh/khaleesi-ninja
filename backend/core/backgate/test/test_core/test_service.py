"""Test the core backgate service."""

# Python.
from unittest.mock import MagicMock

# Django.
from django.test import TestCase

# khaleesi.ninja.
from core.service import Service
from khaleesi.proto.core_backgate_pb2 import SayHelloRequest


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
    response = self.service.SayHello(request, MagicMock())
    # Assert results.
    self.assertIn(name, response.message)
