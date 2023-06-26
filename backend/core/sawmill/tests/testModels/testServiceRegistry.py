"""Test the service registry."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import TransactionTestCase
from khaleesi.proto.core_pb2 import GrpcCallerDetails
from microservice.models.serviceRegistry import (
  SERVICE_REGISTRY,
  ServiceRegistryKhaleesiGate,
  ServiceRegistryKhaleesiService,
  ServiceRegistryGrpcService,
  ServiceRegistryGrpcMethod,
  ServiceRegistryGrpcCall,
)


# noinspection DuplicatedCode
@patch('microservice.models.serviceRegistry.LOGGER')
class ServiceRegistryTestCase(TransactionTestCase):
  """Test the service registry."""

  fixtures = [ 'testServiceRegistry.json' ]

  def testAddingKhaleesiGate(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = 'new-khaleesi-gate'
    callerDetails.khaleesiService = 'new-khaleesi-service'
    callerDetails.grpcService     = 'new-grpc-service'
    callerDetails.grpcMethod      = 'new-grpc-method'
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addService(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount    + 1, ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount + 1, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount     + 1, ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount      + 1, ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryKhaleesiGate.objects.get(name = callerDetails.khaleesiGate)
    ServiceRegistryKhaleesiService.objects.get(name = callerDetails.khaleesiService)
    ServiceRegistryGrpcService.objects.get(name = callerDetails.grpcService)
    ServiceRegistryGrpcMethod.objects.get(name = callerDetails.grpcMethod)

  def testAddingKhaleesiService(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = 'khaleesi-gate-1'
    callerDetails.khaleesiService = 'new-khaleesi-service'
    callerDetails.grpcService     = 'new-grpc-service'
    callerDetails.grpcMethod      = 'new-grpc-method'
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addService(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount       , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount + 1, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount     + 1, ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount      + 1, ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryKhaleesiService.objects.get(name = callerDetails.khaleesiService)
    ServiceRegistryGrpcService.objects.get(name = callerDetails.grpcService)
    ServiceRegistryGrpcMethod.objects.get(name = callerDetails.grpcMethod)

  def testAddingGrpcService(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = 'khaleesi-gate-1'
    callerDetails.khaleesiService = 'khaleesi-service-1'
    callerDetails.grpcService     = 'new-grpc-service'
    callerDetails.grpcMethod      = 'new-grpc-method'
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addService(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount + 1, ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount  + 1, ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryGrpcService.objects.get(name = callerDetails.grpcService)
    ServiceRegistryGrpcMethod.objects.get( name = callerDetails.grpcMethod)

  def testAddingGrpcMethod(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = 'khaleesi-gate-1'
    callerDetails.khaleesiService = 'khaleesi-service-1'
    callerDetails.grpcService     = 'grpc-service-1'
    callerDetails.grpcMethod      = 'new-grpc-method'
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addService(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount  + 1, ServiceRegistryGrpcMethod.objects.count())
    ServiceRegistryGrpcMethod.objects.get(name = callerDetails.grpcMethod)

  def testAddCall(self, *_: MagicMock) -> None :
    """Test adding a call."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = 'khaleesi-gate-1'
    callerDetails.khaleesiService = 'khaleesi-service-1'
    callerDetails.grpcService     = 'grpc-service-1'
    callerDetails.grpcMethod      = 'grpc-method-1'
    calledDetails = GrpcCallerDetails()
    calledDetails.khaleesiGate    = 'khaleesi-gate-2'
    calledDetails.khaleesiService = 'khaleesi-service-3'
    calledDetails.grpcService     = 'grpc-service-3'
    calledDetails.grpcMethod      = 'grpc-method-3'
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    callCount            = ServiceRegistryGrpcCall.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addCall(callerDetails = callerDetails, calledDetails = calledDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount     , ServiceRegistryGrpcMethod.objects.count())
    self.assertEqual(callCount + 1       , ServiceRegistryGrpcCall.objects.count())
    ServiceRegistryGrpcCall.objects.get(
      caller__name = callerDetails.grpcMethod,
      called__name = calledDetails.grpcMethod,
    )

  def testReload(self, *_: MagicMock) -> None :
    """Test reloading the registry."""
    # Execute test.
    SERVICE_REGISTRY.reload()
    # Assert result.
    for i in range(1, 3):
      self._registryContainsKGate(number = i)
    for i in range(1, 4):
      self._registryContainsKService(number = i)
    for i in range(1, 5):
      self._registryContainsGService(number = i)
    for i in range(1, 6):
      self._registryContainsGMethod(number = i)

    self.assertIn(
      'grpc-method-2',
      SERVICE_REGISTRY.cache.get('service-registry')['khaleesi-gate-1'].services[
        'khaleesi-service-1'
      ].services['grpc-service-1'].methods['grpc-method-1'].calls['khaleesi-gate-2'].services[
        'khaleesi-service-2'
      ].services['grpc-service-2'].methods,
    )

  def testAddServiceExitEarly(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addService(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount     , ServiceRegistryGrpcMethod.objects.count())

  def testAddCallExitEarlyCaller(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addCall(callerDetails = callerDetails, calledDetails = callerDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount     , ServiceRegistryGrpcMethod.objects.count())

  def testAddCallExitEarlyCalled(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = 'khaleesi-gate-1'
    callerDetails.khaleesiService = 'khaleesi-service-1'
    callerDetails.grpcService     = 'grpc-service-1'
    callerDetails.grpcMethod      = 'grpc-method-1'
    calledDetails = GrpcCallerDetails()
    khaleesiGateCount    = ServiceRegistryKhaleesiGate.objects.count()
    khaleesiServiceCount = ServiceRegistryKhaleesiService.objects.count()
    grpcServiceCount     = ServiceRegistryGrpcService.objects.count()
    grpcMethodCount      = ServiceRegistryGrpcMethod.objects.count()
    SERVICE_REGISTRY.reload()
    # Execute test.
    SERVICE_REGISTRY.addCall(callerDetails = callerDetails, calledDetails = calledDetails)
    # Assert result.
    self.assertEqual(khaleesiGateCount   , ServiceRegistryKhaleesiGate.objects.count())
    self.assertEqual(khaleesiServiceCount, ServiceRegistryKhaleesiService.objects.count())
    self.assertEqual(grpcServiceCount    , ServiceRegistryGrpcService.objects.count())
    self.assertEqual(grpcMethodCount     , ServiceRegistryGrpcMethod.objects.count())

  def testGetCallData(self, *_: MagicMock) -> None :
    """Test fetching the call data for a given khaleesi service."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = 'khaleesi-gate-1'
    callerDetails.khaleesiService = 'khaleesi-service-1'
    callerDetails.grpcService     = 'grpc-service-1'
    callerDetails.grpcMethod      = 'grpc-method-1'
    calls                         = 'grpc-method-2'
    # Execute test.
    result = SERVICE_REGISTRY.getCallData(owner = callerDetails)
    # Assert result.
    self.assertEqual(1, len(result.callList))
    self.assertEqual(1, len(result.callList[0].calls))
    self.assertEqual(0, len(result.callList[0].calledBy))
    self.assertEqual(callerDetails.grpcMethod, result.callList[0].call.grpcMethod)
    self.assertEqual(calls                   , result.callList[0].calls[0].grpcMethod)

  @patch.object(SERVICE_REGISTRY, 'cache')
  def testGetServiceRegistryNoCache(self, cache: MagicMock, *_: MagicMock) -> None :
    """Test instantiation."""
    # Prepare data.
    cache.get.return_value = None
    # Execute result.
    result = SERVICE_REGISTRY.getServiceRegistry()
    # Assert result.
    self.assertEqual({}, result)

  def _registryContainsKGate(self, *, number: int) -> None :
    self.assertIsNotNone(SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{number}'])

  def _registryContainsKService(self, *, number: int) -> None :
    khaleesiGate = min(number, 2)
    self.assertIn(
      f'khaleesi-service-{number}',
      SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{khaleesiGate}'].services,
    )

  def _registryContainsGService(self, *, number: int) -> None :
    khaleesiGate = min(number, 2)
    khaleesiService = min(number, 3)
    self.assertIn(
      f'grpc-service-{number}',
      SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{khaleesiGate}'].services[
        f'khaleesi-service-{khaleesiService}'
      ].services,
    )

  def _registryContainsGMethod(self, *, number: int) -> None :
    khaleesiGate = min(number, 2)
    khaleesiService = min(number, 3)
    grpcService = min(number, 4)
    self.assertIn(
      f'grpc-method-{number}',
      SERVICE_REGISTRY.cache.get('service-registry')[f'khaleesi-gate-{khaleesiGate}'].services[
        f'khaleesi-service-{khaleesiService}'
      ].services[f'grpc-service-{grpcService}'].methods,
    )
