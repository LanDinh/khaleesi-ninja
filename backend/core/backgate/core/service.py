"""Core Backgate Service"""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.proto.core_backgate_pb2 import DESCRIPTOR, SayHelloRequest, SayHelloResponse
from khaleesi.proto.core_backgate_pb2_grpc import GateKeeperServicer, add_GateKeeperServicer_to_server  # pylint: disable=line-too-long


class Service(GateKeeperServicer):
  """Core Backgate Service"""

  def SayHello(self, request: SayHelloRequest, _: grpc.ServicerContext) -> SayHelloResponse :  # pylint: disable=invalid-name,no-self-use
    """Says hello."""
    return SayHelloResponse(message = f'Hello {request.name}')


def register_handler(server: grpc.Server) -> None :
  """Register the handler."""
  add_GateKeeperServicer_to_server(Service(), server)  # type: ignore[no-untyped-call]

full_name = DESCRIPTOR.services_by_name['GateKeeper'].full_name

service_configuration = (full_name, register_handler)
