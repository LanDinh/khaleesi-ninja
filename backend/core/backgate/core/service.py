"""Core Backgate Service"""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.proto.core_backgate_pb2 import DESCRIPTOR, SayHelloRequest, SayHelloResponse
from khaleesi.proto.core_backgate_pb2_grpc import ServiceServicer, add_ServiceServicer_to_server


class Service(ServiceServicer):
  """Core Backgate Service"""

  def SayHello(self, request: SayHelloRequest, context: grpc.ServicerContext):
    """Says hello."""
    return SayHelloResponse(message = f'Hello {request.name}')


def register_handler(server):
  add_ServiceServicer_to_server(Service(), server)

full_name = DESCRIPTOR.services_by_name['Service'].full_name

service_configuration = (full_name, register_handler)
