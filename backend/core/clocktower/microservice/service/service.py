"""core_clocktower service."""

# gRPC.
#import grpc

# khaleesi-ninja.
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_clocktower_pb2 import DESCRIPTOR
from khaleesi.proto.core_clocktower_pb2_grpc import (
#    BellRingerStub,
    BellRingerServicer as Servicer,
    add_BellRingerServicer_to_server as add_to_server
)
# from microservice.models import SomeModel


class Service(Servicer):
  """core_clocktower service."""

  #def SomeMethod(self, request: SomeRequest, _: grpc.ServicerContext) -> SomeResponse :
  #  """Does something."""
  #  channel = grpc.insecure_channel("some-micro-service:8000")
  #  client = SomeStub(channel)
  #  response = client.SomeMethod(request)
  #  return SomeResponse()


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['SomeService'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
