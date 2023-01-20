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
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.proto.core_pb2 import GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import ServiceCallData, CallData


class ServiceRegistryKhaleesiGate(models.Model):
  """Gates."""
  name = models.TextField(unique = True)


class ServiceRegistryKhaleesiService(models.Model):
  """Gates."""
  name = models.TextField()
  khaleesi_gate = models.ForeignKey(
    ServiceRegistryKhaleesiGate,
    on_delete = models.CASCADE,
    related_name = 'khaleesi_services',
  )
  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'khaleesi_gate' ],
      name   = 'unique_khaleesi_service',
    )]


class ServiceRegistryGrpcService(models.Model):
  """Gates."""
  name    = models.TextField()
  khaleesi_service = models.ForeignKey(
    ServiceRegistryKhaleesiService,
    on_delete = models.CASCADE,
    related_name = 'grpc_services',
  )
  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'khaleesi_service' ],
      name   = 'unique_grpc_service',
    )]


class ServiceRegistryGrpcMethod(models.Model):
  """Gates."""
  name    = models.TextField()
  grpc_service = models.ForeignKey(
    ServiceRegistryGrpcService,
    on_delete = models.CASCADE,
    related_name = 'grpc_methods',
  )
  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'grpc_service' ],
      name   = 'unique_grpc_method',
    )]


class ServiceRegistryGrpcCall(models.Model):
  """Map calls."""
  caller = models.ForeignKey(
    ServiceRegistryGrpcMethod,
    on_delete = models.CASCADE,
    related_name = 'called_by',
  )
  called = models.ForeignKey(
    ServiceRegistryGrpcMethod,
    on_delete = models.CASCADE,
    related_name = 'calls',
  )
  class Meta:
    constraints = [ models.UniqueConstraint(fields = [ 'caller', 'called' ], name = 'unique_calls')]


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
  calls     : Dict[str, KhaleesiGate] = field(default_factory = dict)
  called_by : Dict[str, KhaleesiGate] = field(default_factory = dict)


class ServiceRegistry:
  """Service registry."""

  cache = caches['service-registry']

  def add_call(
      self, *,
      caller_details: GrpcCallerDetails,
      called_details: GrpcCallerDetails,
  ) -> None :
    """If the call is not yet in the service_registry, add it."""
    if self._should_exit_early(caller_details = caller_details):
      return
    if self._should_exit_early(caller_details = called_details):
      return

    service_registry = self.get_service_registry()

    should_add_caller = self._should_add_service_registry_entry(
      service_registry = service_registry,
      caller_details = caller_details,
    )
    should_add_called = self._should_add_service_registry_entry(
      service_registry = service_registry,
      caller_details = called_details,
    )

    # If either the caller or the called was added, we always have to add the call, too.
    should_add_call = should_add_caller or should_add_called
    # If neither the caller nor the called was added, we need to check if the call should be added.
    if not should_add_call:
      khaleesi_gate    = service_registry[caller_details.khaleesi_gate]
      khaleesi_service = khaleesi_gate.services[caller_details.khaleesi_service]
      grpc_service     = khaleesi_service.services[caller_details.grpc_service]
      grpc_method      = grpc_service.methods[caller_details.grpc_method]
      should_add_call = self._should_add_service_registry_entry(
          service_registry = grpc_method.calls,
          caller_details = called_details,
      )
    if should_add_call:
      caller = self._get_or_create_entry_for_db(caller_details = caller_details)
      called = self._get_or_create_entry_for_db(caller_details = called_details)
      ServiceRegistryGrpcCall.objects.get_or_create(caller_id = caller.pk, called_id = called.pk)
      self.reload()

  def add_service(self, *, caller_details: GrpcCallerDetails) -> None :
    """If the entry is not yet in the service_registry, add it."""
    if self._should_exit_early(caller_details = caller_details):
      return

    if self._should_add_service_registry_entry(
        service_registry = self.get_service_registry(),
        caller_details = caller_details,
    ):
      self._get_or_create_entry_for_db(caller_details = caller_details)
      self.reload()

  def _should_exit_early(self, *, caller_details: GrpcCallerDetails) -> bool :
    return not (
        caller_details.khaleesi_gate and caller_details.khaleesi_service
        and caller_details.grpc_service and caller_details.grpc_method
    )

  def _should_add_service_registry_entry(
      self, *,
      service_registry: Dict[str, KhaleesiGate],
      caller_details: GrpcCallerDetails,
  ) -> bool :
    khaleesi_gate = service_registry.get(caller_details.khaleesi_gate, None)
    if not khaleesi_gate:
      return True

    khaleesi_service = khaleesi_gate.services.get(caller_details.khaleesi_service, None)
    if not khaleesi_service:
      return True

    grpc_service = khaleesi_service.services.get(caller_details.grpc_service, None)
    if not grpc_service:
      return True

    grpc_method = grpc_service.methods.get(caller_details.grpc_method, None)
    if not grpc_method:
      return True

    return False


  def reload(self) -> None :
    """Reload the service registry from the DB."""
    calls = ServiceRegistryGrpcCall.objects.all().select_related(
      'caller__grpc_service__khaleesi_service__khaleesi_gate',
      'called__grpc_service__khaleesi_service__khaleesi_gate',
    )
    methods = ServiceRegistryGrpcMethod.objects.all().select_related(
      'grpc_service__khaleesi_service__khaleesi_gate',
    )
    service_registry: Dict[str, KhaleesiGate] = {}

    # There might be some methods without calls, so add them first.
    for method in methods:
      self._reload_grpc_method(service_registry = service_registry, method = method)

    for call in calls:
      caller = self._reload_grpc_method(service_registry = service_registry, method = call.caller)
      called = self._reload_grpc_method(service_registry = service_registry, method = call.called)
      self._reload_grpc_method(service_registry = caller.calls    , method = call.called)
      self._reload_grpc_method(service_registry = called.called_by, method = call.caller)

    self.cache.clear()
    self.cache.set('service-registry', service_registry)

    LOGGER.debug(f'Service registry reloaded: {len(methods)} entries, {len(calls)} calls')

  def get_call_data(self, *, owner: GrpcCallerDetails) -> ServiceCallData :
    """Get call data for the affected service."""
    service_call_data = ServiceCallData()
    self.add_service(caller_details = owner)
    own_service = self.get_service_registry()[owner.khaleesi_gate].services[owner.khaleesi_service]

    for service_name, service in own_service.services.items():
      for method_name, method in service.methods.items():
        call_data = CallData()
        call_data.call.khaleesi_gate    = owner.khaleesi_gate
        call_data.call.khaleesi_service = owner.khaleesi_service
        call_data.call.grpc_service     = service_name
        call_data.call.grpc_method      = method_name
        self._add_data_to_call(full_list = method.calls    , result_list = call_data.calls)
        self._add_data_to_call(full_list = method.called_by, result_list = call_data.called_by)
        service_call_data.call_list.append(call_data)

    return service_call_data

  def _add_data_to_call(
      self, *,
      full_list: Dict[str, KhaleesiGate],
      result_list: RepeatedCompositeFieldContainer[GrpcCallerDetails],
  ) -> None :
    for khaleesi_gate_name, khaleesi_gate in full_list.items():
      for khaleesi_service_name, khaleesi_service in khaleesi_gate.services.items():
        for grpc_service_name, grpc_service in khaleesi_service.services.items():
          for grpc_method_name, _ in grpc_service.methods.items():
            called = GrpcCallerDetails()
            called.khaleesi_gate    = khaleesi_gate_name
            called.khaleesi_service = khaleesi_service_name
            called.grpc_service     = grpc_service_name
            called.grpc_method      = grpc_method_name
            result_list.append(called)

  def _reload_grpc_method(
      self, *,
      service_registry: Dict[str, KhaleesiGate],
      method: ServiceRegistryGrpcMethod,
  ) -> GrpcMethod :
    khaleesi_gate = self._get_or_create_dict_entry(
      data = service_registry,
      key = method.grpc_service.khaleesi_service.khaleesi_gate.name,
      value = KhaleesiGate()
    )
    khaleesi_service = self._get_or_create_dict_entry(
      data = khaleesi_gate.services,
      key = method.grpc_service.khaleesi_service.name,
      value = KhaleesiService()
    )
    grpc_service = self._get_or_create_dict_entry(
      data = khaleesi_service.services,
      key = method.grpc_service.name,
      value = GrpcService()
    )
    return self._get_or_create_dict_entry(
      data = grpc_service.methods,
      key = method.name,
      value = GrpcMethod()
    )


  def get_service_registry(self) -> Dict[str, KhaleesiGate] :
    """Get the service registry."""
    service_registry: Dict[str, KhaleesiGate] = self.cache.get('service-registry')
    if not service_registry:
      service_registry = {}
      self.cache.set('service-registry', service_registry)
    return service_registry

  def _get_or_create_dict_entry(self, *, data: Dict[str, T], key: str, value: T) -> T :
    if not key in data:
      data[key] = value
    return data[key]

  def _get_or_create_entry_for_db(
      self, *,
      caller_details: GrpcCallerDetails,
  ) -> ServiceRegistryGrpcMethod :
    LOGGER.debug(
      'Add new service registry entry: '
      f'{caller_details.khaleesi_gate} {caller_details.khaleesi_service} '
      f'{caller_details.grpc_service} {caller_details.grpc_method}')

    khaleesi_gate, _ = ServiceRegistryKhaleesiGate.objects.get_or_create(
      name = caller_details.khaleesi_gate,
    )
    khaleesi_service, _ = ServiceRegistryKhaleesiService.objects.get_or_create(
      name              = caller_details.khaleesi_service,
      khaleesi_gate_id = khaleesi_gate.pk,
    )
    grpc_service, _ = ServiceRegistryGrpcService.objects.get_or_create(
      name                 = caller_details.grpc_service,
      khaleesi_service_id = khaleesi_service.pk,
    )
    grpc_method, _ = ServiceRegistryGrpcMethod.objects.get_or_create(
      name             = caller_details.grpc_method,
      grpc_service_id = grpc_service.pk,
    )
    return grpc_method


SERVICE_REGISTRY = ServiceRegistry()
