"""Test the core guard service."""

# Python.
from unittest.mock import MagicMock

# Django.
from django.test import TransactionTestCase

# khaleesi.ninja.
from microservice.models import TestModel
from microservice.service import Service
from khaleesi.proto.core_backgate_pb2 import SayHelloRequest


class CoreGuardServiceTestCase(TransactionTestCase):
  """Test the core backgate service."""

  databases = {'read', 'write'}

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
    self.assertEqual(1, TestModel.objects.count())
    self.assertIn(name, TestModel.objects.get().text)
