"""Service registry."""

# Python.
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, TypeVar

# Django.
from django.core.cache import caches
from django.db import models

# gRPC.
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.proto.core_pb2 import GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import ServiceCallData, CallData


class ServiceRegistryKhaleesiGate(models.Model):
  """Gates."""
  name = models.TextField(unique = True)


class ServiceRegistryKhaleesiService(models.Model):
  """Gates."""
  name = models.TextField()
  khaleesiGate = models.ForeignKey(
    ServiceRegistryKhaleesiGate,
    on_delete    = models.CASCADE,
    related_name = 'khaleesiServices',
  )

  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'khaleesiGate' ],
      name   = 'uniqueKhaleesiService',
    )]


class ServiceRegistryGrpcService(models.Model):
  """Gates."""
  name    = models.TextField()
  khaleesiService = models.ForeignKey(
    ServiceRegistryKhaleesiService,
    on_delete    = models.CASCADE,
    related_name = 'grpcServices',
  )

  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'khaleesiService' ],
      name   = 'uniqueGrpcService',
    )]


class ServiceRegistryGrpcMethod(models.Model):
  """Gates."""
  name    = models.TextField()
  grpcService = models.ForeignKey(
    ServiceRegistryGrpcService,
    on_delete    = models.CASCADE,
    related_name = 'grpcMethods',
  )

  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'grpcService' ],
      name   = 'uniqueGrpcMethod',
    )]


class ServiceRegistryGrpcCall(models.Model):
  """Map calls."""
  caller = models.ForeignKey(
    ServiceRegistryGrpcMethod,
    on_delete    = models.CASCADE,
    related_name = 'calledBy',
  )
  called = models.ForeignKey(
    ServiceRegistryGrpcMethod,
    on_delete    = models.CASCADE,
    related_name = 'calls',
  )

  class Meta:
    constraints = [ models.UniqueConstraint(fields = [ 'caller', 'called' ], name = 'uniqueCalls')]


T = TypeVar('T')


@dataclass
class KhaleesiGate:
  """Simple representation of the gates."""
  services : Dict[str, KhaleesiService] = field(default_factory = dict)

@dataclass
class KhaleesiService:
  """Simple representation of the khaleesi services."""
  services : Dict[str, GrpcService] = field(default_factory = dict)

@dataclass
class GrpcService:
  """Simple representation of the grpc services."""
  methods : Dict[str, GrpcMethod] = field(default_factory = dict)

@dataclass
class GrpcMethod:
  """Simple representation of the grpc methods."""
  calls   : Dict[str, KhaleesiGate] = field(default_factory = dict)
  calledBy: Dict[str, KhaleesiGate] = field(default_factory = dict)


class ServiceRegistry:
  """Service registry."""

  cache = caches['service-registry']

  def addCall(self, *, callerDetails: GrpcCallerDetails, calledDetails: GrpcCallerDetails) -> None :
    """If the call is not yet in the serviceRegistry, add it."""
    if self._shouldExitEarly(callerDetails = callerDetails):
      return
    if self._shouldExitEarly(callerDetails = calledDetails):
      return

    serviceRegistry = self.getServiceRegistry()

    shouldAddCaller = self._shouldAddServiceRegistryEntry(
      serviceRegistry = serviceRegistry,
      callerDetails   = callerDetails,
    )
    shouldAddCalled = self._shouldAddServiceRegistryEntry(
      serviceRegistry = serviceRegistry,
      callerDetails   = calledDetails,
    )

    # If either the caller or the called was added, we always have to add the call, too.
    shouldAddCall = shouldAddCaller or shouldAddCalled
    # If neither the caller nor the called was added, we need to check if the call should be added.
    if not shouldAddCall:
      khaleesiGate    = serviceRegistry[callerDetails.khaleesiGate]
      khaleesiService = khaleesiGate.services[callerDetails.khaleesiService]
      grpcService     = khaleesiService.services[callerDetails.grpcService]
      grpcMethod      = grpcService.methods[callerDetails.grpcMethod]
      shouldAddCall = self._shouldAddServiceRegistryEntry(
          serviceRegistry = grpcMethod.calls,
          callerDetails   = calledDetails,
      )
    if shouldAddCall:
      caller = self._getOrCreateEntryForDb(callerDetails = callerDetails)
      called = self._getOrCreateEntryForDb(callerDetails = calledDetails)
      ServiceRegistryGrpcCall.objects.get_or_create(caller_id = caller.pk, called_id = called.pk)
      self.reload()

  def addService(self, *, callerDetails: GrpcCallerDetails) -> None :
    """If the entry is not yet in the serviceRegistry, add it."""
    if self._shouldExitEarly(callerDetails = callerDetails):
      return

    if self._shouldAddServiceRegistryEntry(
        serviceRegistry = self.getServiceRegistry(),
        callerDetails   = callerDetails,
    ):
      self._getOrCreateEntryForDb(callerDetails = callerDetails)
      self.reload()

  def _shouldExitEarly(self, *, callerDetails: GrpcCallerDetails) -> bool :
    return not (
        callerDetails.khaleesiGate and callerDetails.khaleesiService
        and callerDetails.grpcService and callerDetails.grpcMethod
    )

  def _shouldAddServiceRegistryEntry(
      self, *,
      serviceRegistry: Dict[str, KhaleesiGate],
      callerDetails  : GrpcCallerDetails,
  ) -> bool :
    khaleesiGate = serviceRegistry.get(callerDetails.khaleesiGate, None)
    if not khaleesiGate:
      return True

    khaleesiService = khaleesiGate.services.get(callerDetails.khaleesiService, None)
    if not khaleesiService:
      return True

    grpcService = khaleesiService.services.get(callerDetails.grpcService, None)
    if not grpcService:
      return True

    grpcMethod = grpcService.methods.get(callerDetails.grpcMethod, None)
    if not grpcMethod:
      return True

    return False


  def reload(self) -> None :
    """Reload the service registry from the DB."""
    calls = ServiceRegistryGrpcCall.objects.all().select_related(
      'caller__grpcService__khaleesiService__khaleesiGate',
      'called__grpcService__khaleesiService__khaleesiGate',
    )
    methods = ServiceRegistryGrpcMethod.objects.all().select_related(
      'grpcService__khaleesiService__khaleesiGate',
    )
    serviceRegistry: Dict[str, KhaleesiGate] = {}

    # There might be some methods without calls, so add them first.
    for method in methods:
      self._reloadGrpcMethod(serviceRegistry = serviceRegistry, method = method)

    for call in calls:
      caller = self._reloadGrpcMethod(serviceRegistry = serviceRegistry, method = call.caller)
      called = self._reloadGrpcMethod(serviceRegistry = serviceRegistry, method = call.called)
      self._reloadGrpcMethod(serviceRegistry = caller.calls   , method = call.called)
      self._reloadGrpcMethod(serviceRegistry = called.calledBy, method = call.caller)

    self.cache.clear()
    self.cache.set('service-registry', serviceRegistry)

    LOGGER.debug(f'Service registry reloaded: {len(methods)} entries, {len(calls)} calls')

  def getCallData(self, *, owner: GrpcCallerDetails) -> ServiceCallData :
    """Get call data for the affected service."""
    serviceCallData = ServiceCallData()
    self.addService(callerDetails = owner)
    ownService = self.getServiceRegistry()[owner.khaleesiGate].services[owner.khaleesiService]

    for serviceName, service in ownService.services.items():
      for methodName, method in service.methods.items():
        callData = CallData()
        callData.call.khaleesiGate    = owner.khaleesiGate
        callData.call.khaleesiService = owner.khaleesiService
        callData.call.grpcService     = serviceName
        callData.call.grpcMethod      = methodName
        self._addDataToCall(fullList = method.calls   , resultList = callData.calls)
        self._addDataToCall(fullList = method.calledBy, resultList = callData.calledBy)
        serviceCallData.callList.append(callData)

    return serviceCallData

  def _addDataToCall(
      self, *,
      fullList  : Dict[str, KhaleesiGate],
      resultList: RepeatedCompositeFieldContainer[GrpcCallerDetails],
  ) -> None :
    for khaleesiGateName, khaleesiGate in fullList.items():
      for khaleesiServiceName, khaleesiService in khaleesiGate.services.items():
        for grpcServiceName, grpcService in khaleesiService.services.items():
          for grpcMethodName, _ in grpcService.methods.items():
            called = GrpcCallerDetails()
            called.khaleesiGate    = khaleesiGateName
            called.khaleesiService = khaleesiServiceName
            called.grpcService     = grpcServiceName
            called.grpcMethod      = grpcMethodName
            resultList.append(called)

  def _reloadGrpcMethod(
      self, *,
      serviceRegistry: Dict[str, KhaleesiGate],
      method         : ServiceRegistryGrpcMethod,
  ) -> GrpcMethod :
    khaleesiGate = self._getOrCreateDictEntry(
      data  = serviceRegistry,
      key   = method.grpcService.khaleesiService.khaleesiGate.name,
      value = KhaleesiGate()
    )
    khaleesiService = self._getOrCreateDictEntry(
      data  = khaleesiGate.services,
      key   = method.grpcService.khaleesiService.name,
      value = KhaleesiService()
    )
    grpcService = self._getOrCreateDictEntry(
      data  = khaleesiService.services,
      key   = method.grpcService.name,
      value = GrpcService()
    )
    return self._getOrCreateDictEntry(
      data  = grpcService.methods,
      key   = method.name,
      value = GrpcMethod()
    )


  def getServiceRegistry(self) -> Dict[str, KhaleesiGate] :
    """Get the service registry."""
    serviceRegistry: Dict[str, KhaleesiGate] = self.cache.get('service-registry')
    if not serviceRegistry:
      serviceRegistry = {}
      self.cache.set('service-registry', serviceRegistry)
    return serviceRegistry

  def _getOrCreateDictEntry(self, *, data: Dict[str, T], key: str, value: T) -> T :
    if not key in data:
      data[key] = value
    return data[key]

  def _getOrCreateEntryForDb(
      self, *,
      callerDetails: GrpcCallerDetails,
  ) -> ServiceRegistryGrpcMethod :
    LOGGER.debug(
      'Add new service registry entry: '
      f'{callerDetails.khaleesiGate} {callerDetails.khaleesiService} '
      f'{callerDetails.grpcService} {callerDetails.grpcMethod}')

    khaleesiGate, _ = ServiceRegistryKhaleesiGate.objects.get_or_create(
      name = callerDetails.khaleesiGate,
    )
    khaleesiService,  _ = ServiceRegistryKhaleesiService.objects.get_or_create(
      name            = callerDetails.khaleesiService,
      khaleesiGate_id = khaleesiGate.pk,
    )
    grpcService, _ = ServiceRegistryGrpcService.objects.get_or_create(
      name               = callerDetails.grpcService,
      khaleesiService_id = khaleesiService.pk,
    )
    grpcMethod, _ = ServiceRegistryGrpcMethod.objects.get_or_create(
      name           = callerDetails.grpcMethod,
      grpcService_id = grpcService.pk,
    )
    return grpcMethod


SERVICE_REGISTRY = ServiceRegistry()
