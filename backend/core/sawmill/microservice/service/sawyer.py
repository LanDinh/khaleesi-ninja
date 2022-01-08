"""core-sawmill service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import DESCRIPTOR, LogFilter, EventsList
from khaleesi.proto.core_sawmill_pb2_grpc import (
  SawyerServicer as Servicer,
  add_SawyerServicer_to_server as add_to_server
)
from microservice.models import Event as DbEvent


class Service(Servicer):
  """core-sawmill service."""

  def GetEvents(self, request: LogFilter, _: grpc.ServicerContext) -> EventsList :
    """Get logged events."""
    result = EventsList()
    for event in DbEvent.objects.all():
      result.events.append(event.to_grpc_event())
    return result


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Sawyer'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
