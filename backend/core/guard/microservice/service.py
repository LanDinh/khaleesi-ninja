"""Core Backgate Service"""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.service_configuration import ServiceConfiguration
from khaleesi.proto.core_backgate_pb2 import DESCRIPTOR, SayHelloRequest, SayHelloResponse
from khaleesi.proto.core_backgate_pb2_grpc import GateKeeperServicer, add_GateKeeperServicer_to_server  # pylint: disable=line-too-long
from microservice.models import TestModel


class Service(GateKeeperServicer):
  """Core Backgate Service"""

  def SayHello(self, request: SayHelloRequest, _: grpc.ServicerContext) -> SayHelloResponse :
    """Says hello."""
    text = TestModel(text = f'Hello {request.name}')
    text.save()
    return SayHelloResponse(message = text.text)


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['GateKeeper'].full_name,
  add_service_to_server = add_GateKeeperServicer_to_server,
  service = Service()
)
