"""core-sawmill service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import DESCRIPTOR, LogFilter, EventsList, RequestList
from khaleesi.proto.core_sawmill_pb2_grpc import (
  SawyerServicer as Servicer,
  add_SawyerServicer_to_server as add_to_server
)
from microservice.models import Event as DbEvent, Request as DbRequest


class Service(Servicer):
  """core-sawmill service."""

  def GetEvents(self, request: LogFilter, _: grpc.ServicerContext) -> EventsList :
    """Get logged events."""
    result = EventsList()
    for event in DbEvent.objects.filter():
      result.events.append(event.to_grpc_event_response())
    return result

  def GetRequests(self, request: LogFilter, _: grpc.ServicerContext) -> RequestList :
    result = RequestList()
    for db_request in DbRequest.objects.filter():
      result.requests.append(db_request.to_grpc_request_response())
    return result


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Sawyer'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
