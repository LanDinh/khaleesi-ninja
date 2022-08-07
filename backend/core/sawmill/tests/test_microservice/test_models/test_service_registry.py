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
  ServiceRegistryGrpcCall,
)


# noinspection DuplicatedCode
@patch('microservice.models.service_registry.LOGGER')
class ServiceRegistryTestCase(TransactionTestCase):
  """Test the service registry."""

  fixtures = [ 'test_service_registry.json' ]

  def test_adding_khaleesi_gate(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'new-khaleesi-gate'
    caller_details.khaleesi_service = 'new-khaleesi-service'
    caller_details.grpc_service     = 'new-grpc-service'
    caller_details.grpc_method      = 'new-grpc-method'
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_service(caller_details = caller_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count + 1   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count + 1, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count + 1    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count + 1     , ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryKhaleesiGate.objects.get(   name = caller_details.khaleesi_gate)
    ServiceRegistryKhaleesiService.objects.get(name = caller_details.khaleesi_service)
    ServiceRegistryGrpcService.objects.get(    name = caller_details.grpc_service)
    ServiceRegistryGrpcMethod.objects.get(     name = caller_details.grpc_method)

  def test_adding_khaleesi_service(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'khaleesi-gate-1'
    caller_details.khaleesi_service = 'new-khaleesi-service'
    caller_details.grpc_service     = 'new-grpc-service'
    caller_details.grpc_method      = 'new-grpc-method'
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_service(caller_details = caller_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count       , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count + 1, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count + 1    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count + 1     , ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryKhaleesiService.objects.get(name = caller_details.khaleesi_service)
    ServiceRegistryGrpcService.objects.get(    name = caller_details.grpc_service)
    ServiceRegistryGrpcMethod.objects.get(     name = caller_details.grpc_method)

  def test_adding_grpc_service(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'khaleesi-gate-1'
    caller_details.khaleesi_service = 'khaleesi-service-1'
    caller_details.grpc_service     = 'new-grpc-service'
    caller_details.grpc_method      = 'new-grpc-method'
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_service(caller_details = caller_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count + 1, ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count + 1 , ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryGrpcService.objects.get(name = caller_details.grpc_service)
    ServiceRegistryGrpcMethod.objects.get( name = caller_details.grpc_method)

  def test_adding_grpc_method(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'khaleesi-gate-1'
    caller_details.khaleesi_service = 'khaleesi-service-1'
    caller_details.grpc_service     = 'grpc-service-1'
    caller_details.grpc_method      = 'new-grpc-method'
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_service(caller_details = caller_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count + 1 , ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryGrpcMethod.objects.get(name = caller_details.grpc_method)

  def test_add_call(self, *_: MagicMock) -> None :
    """Test adding a call."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'khaleesi-gate-1'
    caller_details.khaleesi_service = 'khaleesi-service-1'
    caller_details.grpc_service     = 'grpc-service-1'
    caller_details.grpc_method      = 'grpc-method-1'
    called_details = GrpcCallerDetails()
    called_details.khaleesi_gate    = 'khaleesi-gate-2'
    called_details.khaleesi_service = 'khaleesi-service-3'
    called_details.grpc_service     = 'grpc-service-3'
    called_details.grpc_method      = 'grpc-method-3'
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    call_count             = ServiceRegistryGrpcCall.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_call(caller_details = caller_details, called_details = called_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count     , ServiceRegistryGrpcMethod.objects.count())
    self.assertEqual(call_count + 1        , ServiceRegistryGrpcCall.objects.count())
    ServiceRegistryGrpcCall.objects.get(
      caller__name = caller_details.grpc_method,
      called__name = called_details.grpc_method,
    )

  def test_reload(self, *_: MagicMock) -> None :
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

    self.assertIn(
      'grpc-method-2',
      SERVICE_REGISTRY.cache.get('service-registry')['khaleesi-gate-1'].services[
        'khaleesi-service-1'
      ].services['grpc-service-1'].methods['grpc-method-1'].calls['khaleesi-gate-2'].services[
        'khaleesi-service-2'
      ].services['grpc-service-2'].methods,
    )

  def test_add_service_exit_early(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_service(caller_details = caller_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count     , ServiceRegistryGrpcMethod.objects.count())

  def test_add_call_exit_early_caller(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_call(caller_details = caller_details, called_details = caller_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count     , ServiceRegistryGrpcMethod.objects.count())

  def test_add_call_exit_early_called(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'khaleesi-gate-1'
    caller_details.khaleesi_service = 'khaleesi-service-1'
    caller_details.grpc_service     = 'grpc-service-1'
    caller_details.grpc_method      = 'grpc-method-1'
    called_details = GrpcCallerDetails()
    khaleesi_gate_count    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesi_service_count = ServiceRegistryKhaleesiService.objects.count()
    grpc_service_count     = ServiceRegistryGrpcService.objects.count()
    grpc_method_count      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.add_call(caller_details = caller_details, called_details = called_details)
    # Assert result.
    self.assertEqual(khaleesi_gate_count   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesi_service_count, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpc_service_count    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpc_method_count     , ServiceRegistryGrpcMethod.objects.count())

  def test_get_call_data(self, *_: MagicMock) -> None :
    """Test fetching the call data for a given khaleesi service."""
    # Prepare data.
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = 'khaleesi-gate-1'
    caller_details.khaleesi_service = 'khaleesi-service-1'
    caller_details.grpc_service     = 'grpc-service-1'
    caller_details.grpc_method      = 'grpc-method-1'
    calls                           = 'grpc-method-2'
    # Execute test.
    result = SERVICE_REGISTRY.get_call_data(owner = caller_details)
    # Assert result.
    self.assertEqual(1, len(result.call_list))
    self.assertEqual(1, len(result.call_list[0].calls))
    self.assertEqual(0, len(result.call_list[0].called_by))
    self.assertEqual(caller_details.grpc_method, result.call_list[0].call.grpc_method)
    self.assertEqual(calls                     , result.call_list[0].calls[0].grpc_method)

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
