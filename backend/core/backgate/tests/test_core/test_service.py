"""Test the core backgate service."""

# Python.
from unittest.mock import MagicMock, patch

# Grpc.
import grpc

# khaleesi.ninja.
from core.service import Service
from khaleesi.core.test_util.test_case import TransactionTestCase
from khaleesi.proto.core_backgate_pb2 import SayHelloRequest


class CoreBackgateServiceTestCase(TransactionTestCase):
  """Test the core backgate service."""

  databases = {'read', 'write'}

  def setUp(self) -> None :
    """Instantiate the service."""
    self.service =  Service()

  @patch.object(grpc, 'insecure_channel')
  def test_say_hello(self, _: MagicMock) -> None :
    """Test saying hello."""
    # Prepare data.
    name = 'Khaleesi, Mother of Dragons, Breaker of Chains'
    request = SayHelloRequest(name = name)
    # Execute test.
    response = self.service.SayHello(request, MagicMock())
    # Assert result.
    self.assertIn('The guard says:', response.message)
