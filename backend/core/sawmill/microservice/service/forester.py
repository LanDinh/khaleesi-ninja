"""Forester service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.proto.core_pb2 import EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import DESCRIPTOR, ServiceCallData
from khaleesi.proto.core_sawmill_pb2_grpc import (
  ForesterServicer as Servicer,
  add_ForesterServicer_to_server as addToServer
)
from microservice.models.serviceRegistry import SERVICE_REGISTRY


class Service(Servicer):
  """Forester service."""

  def GetServiceCallData(self, request: EmptyRequest, _: grpc.ServicerContext) -> ServiceCallData :
    """Get the call data of the calling service."""
    owner = request.requestMetadata.caller
    LOGGER.info(
      f'Getting service registry call data for {owner.khaleesiGate}-{owner.khaleesiService}.',
    )
    return SERVICE_REGISTRY.getCallData(owner = owner)


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Forester'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
