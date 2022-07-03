"""Service registry."""

# Python.
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, TypeVar

# Django.
from django.core.cache import caches
from django.conf import settings
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.logger import LOGGER
from khaleesi.proto.core_pb2 import GrpcCallerDetails


class ServiceRegistryKhaleesiGate(models.Model):
  """Gates."""
  name = models.TextField()


class ServiceRegistryKhaleesiService(models.Model):
  """Gates."""
  name = models.TextField()
  khaleesi_gate = models.ForeignKey(
    ServiceRegistryKhaleesiGate,
    on_delete = models.CASCADE,
    related_name = 'khaleesi_services',
  )


class ServiceRegistryGrpcService(models.Model):
  """Gates."""
  name    = models.TextField()
  khaleesi_service = models.ForeignKey(
    ServiceRegistryKhaleesiService,
    on_delete = models.CASCADE,
    related_name = 'grpc_services',
  )


class ServiceRegistryGrpcMethod(models.Model):
  """Gates."""
  name    = models.TextField()
  grpc_service = models.ForeignKey(
    ServiceRegistryGrpcService,
    on_delete = models.CASCADE,
    related_name = 'grpc_methods',
  )


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

  def add(self, *, caller_details: GrpcCallerDetails) -> None :
    """If the entry is not yet in the service_registry, add it."""
    service_registry = self.get_service_registry()
    khaleesi_gate = service_registry.get(caller_details.khaleesi_gate, None)
    if not khaleesi_gate:
      self._get_or_create_entry_for_db(caller_details = caller_details)
      return

    khaleesi_service = khaleesi_gate.services.get(caller_details.khaleesi_service, None)
    if not khaleesi_service:
      self._get_or_create_entry_for_db(caller_details = caller_details)
      return

    grpc_service = khaleesi_service.services.get(caller_details.grpc_service, None)
    if not grpc_service:
      self._get_or_create_entry_for_db(caller_details = caller_details)
      return

    grpc_method = grpc_service.methods.get(caller_details.grpc_method, None)
    if not grpc_method:
      self._get_or_create_entry_for_db(caller_details = caller_details)
      return


  def reload(self) -> None :
    """Reload the service registry from the DB."""
    methods = ServiceRegistryGrpcMethod.objects.all().select_related(
      'grpc_service__khaleesi_service__khaleesi_gate',
    )
    service_registry: Dict[str, KhaleesiGate] = {}

    for method in methods:
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
      self._get_or_create_dict_entry(
        data = grpc_service.methods,
        key = method.name,
        value = GrpcMethod()
      )

    self.cache.clear()
    self.cache.set('service-registry', service_registry)

    if settings.DEBUG:
      LOGGER.debug(message = f'Service registry reload: {len(methods)} entries')
      for k_gate_name, k_gate in service_registry.items():
        LOGGER.debug(message = f'    {k_gate_name}')
        for k_service_name, k_service in k_gate.services.items():
          LOGGER.debug(message = f'        {k_service_name}')
          for g_service_name, g_service in k_service.services.items():
            LOGGER.debug(message = f'            {g_service_name}')
            for g_method_name, _ in g_service.methods.items():
              LOGGER.debug(message = f'                {g_method_name}')

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

  def _get_or_create_entry_for_db(self, *, caller_details: GrpcCallerDetails) -> None :
    LOGGER.debug(
      message = 'Add new service registry entry: '
                f'{caller_details.khaleesi_gate} {caller_details.khaleesi_service} '
                f'{caller_details.grpc_service} {caller_details.grpc_method}')

    khaleesi_gate, _ = ServiceRegistryKhaleesiGate.objects.get_or_create(
      name = caller_details.khaleesi_gate,
    )
    khaleesi_service, _ = ServiceRegistryKhaleesiService.objects.get_or_create(
      name          = caller_details.khaleesi_service,
      khaleesi_gate = khaleesi_gate,
    )
    grpc_service, _ = ServiceRegistryGrpcService.objects.get_or_create(
      name             = caller_details.grpc_service,
      khaleesi_service = khaleesi_service,
    )
    ServiceRegistryGrpcMethod.objects.get_or_create(
      name         = caller_details.grpc_method,
      grpc_service = grpc_service,
    )

    self.reload()

SERVICE_REGISTRY = ServiceRegistry()
