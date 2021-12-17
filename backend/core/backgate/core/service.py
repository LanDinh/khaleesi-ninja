"""core-backgate service"""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.service_configuration import ServiceConfiguration
from khaleesi.proto.core_backgate_pb2 import DESCRIPTOR, SayHelloRequest, SayHelloResponse
from khaleesi.proto.core_backgate_pb2_grpc import GateKeeperStub, GateKeeperServicer, add_GateKeeperServicer_to_server  # pylint: disable=line-too-long


class Service(GateKeeperServicer):
  """Core Backgate Service"""

  def SayHello(self, request: SayHelloRequest, _: grpc.ServicerContext) -> SayHelloResponse :  # pylint: disable=invalid-name,no-self-use
    """Says hello."""
    channel = grpc.insecure_channel("core-guard:8000")
    client = GateKeeperStub(channel)  # type: ignore[no-untyped-call]
    response = client.SayHello(request)
    return SayHelloResponse(message = f'The guard says: "{response.message}"')


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['GateKeeper'].full_name,
  add_service_to_server = add_GateKeeperServicer_to_server,
  service = Service()
)
