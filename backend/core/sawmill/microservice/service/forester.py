"""Forester service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.logger import LOGGER
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import DESCRIPTOR, EmptyRequest, ServiceCallData
from khaleesi.proto.core_sawmill_pb2_grpc import (
  ForesterServicer as Servicer,
  add_ForesterServicer_to_server as add_to_server
)
from microservice.models.service_registry import SERVICE_REGISTRY


class Service(Servicer):
  """Forester service."""

  def GetServiceCallData(self, request: EmptyRequest, _: grpc.ServicerContext) -> ServiceCallData :
    """Get the call data of the calling service."""
    LOGGER.info('Getting service registry call data.')
    return SERVICE_REGISTRY.get_call_data(owner = request.request_metadata.caller)


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Forester'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
