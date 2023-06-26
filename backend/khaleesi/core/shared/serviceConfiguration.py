"""gRPC Service Configuration."""

# Python.
from dataclasses import dataclass, field, InitVar
from typing import Callable, TypeVar, Generic

# gRPC.
from grpc import Server


Service = TypeVar('Service')


@dataclass
class ServiceConfiguration(Generic[Service]):
  """gRPC Service Configuration."""

  name              : str
  registerService   : Callable[[Server], None] = field(init = False)
  addServiceToServer: InitVar[Callable[[Service, Server], None]]
  service           : InitVar[Service]

  def __post_init__(
      self,
      addServiceToServer: Callable[[Service, Server], None],
      service           : Service,
  ) -> None :

    def registerService(server: Server) -> None:
      """Register the service to the server."""
      addServiceToServer(service, server)  # pragma: no cover

    self.registerService = registerService
