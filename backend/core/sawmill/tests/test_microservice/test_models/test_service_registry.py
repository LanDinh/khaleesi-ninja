"""Test the service registry."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import TransactionTestCase
from khaleesi.proto.core_pb2 import GrpcCallerDetails
from microservice.models.service_registry import (
  SERVICE_REGISTRY,
  ServiceRegistryKhaleesiGate,
  ServiceRegistryKhaleesiService,
  ServiceRegistryGrpcService,
  ServiceRegistryGrpcMethod,
)

class ServiceRegistryTestCase(TransactionTestCase):
  """Test the service registry."""

  fixtures = [ 'test_service_registry.json' ]

  @patch('microservice.models.service_registry.LOGGER')
  def test_add(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'new-khaleesi-gate'
    caller_details.khaleesi_service = 'new-khaleesi-service'
    caller_details.grpc_service     = 'new-grpc-service'
    caller_details.grpc_method      = 'new-grpc-method'
    # Execute test.
    SERVICE_REGISTRY.add(caller_details = caller_details)
    # Assert result.
    ServiceRegistryKhaleesiGate.objects.get(   name = caller_details.khaleesi_gate)
    ServiceRegistryKhaleesiService.objects.get(name = caller_details.khaleesi_service)
    ServiceRegistryGrpcService.objects.get(    name = caller_details.grpc_service)
    ServiceRegistryGrpcMethod.objects.get(     name = caller_details.grpc_method)

  def test_reload(self) -> None :
    """Test reloading the registry."""
    # Execute test.
    SERVICE_REGISTRY.reload()
    # Assert result.
    for i in range(1, 3):
      self._registry_contains_k_gate(number = i)
    for i in range(1, 4):
      self._registry_contains_k_service(number = i)
    for i in range(1, 5):
      self._registry_contains_g_service(number = i)
    for i in range(1, 6):
      self._registry_contains_g_method(number = i)

  def _registry_contains_k_gate(self, *, number: int) -> None :
    self.assertIsNotNone(SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{number}'])

  def _registry_contains_k_service(self, *, number: int) -> None :
    khaleesi_gate = min(number, 2)
    self.assertIn(
      f'khaleesi-service-{number}',
      SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{khaleesi_gate}'].services,
    )

  def _registry_contains_g_service(self, *, number: int) -> None :
    khaleesi_gate = min(number, 2)
    khaleesi_service = min(number, 3)
    self.assertIn(
      f'grpc-service-{number}',
      SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{khaleesi_gate}'].services[
        f'khaleesi-service-{khaleesi_service}'
      ].services,
    )

  def _registry_contains_g_method(self, *, number: int) -> None :
    khaleesi_gate = min(number, 2)
    khaleesi_service = min(number, 3)
    grpc_service = min(number, 4)
    self.assertIn(
      f'grpc-method-{number}',
      SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{khaleesi_gate}'].services[
        f'khaleesi-service-{khaleesi_service}'
      ].services[f'grpc-service-{grpc_service}'].methods,
    )
