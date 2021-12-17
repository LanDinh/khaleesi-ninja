"""gRPC Service Configuration."""

# Python.
from dataclasses import dataclass, field, InitVar
from typing import Callable, TypeVar, Generic

from grpc import Server


Service = TypeVar('Service')


@dataclass
class ServiceConfiguration(Generic[Service]):
  """gRPC Service Configuration."""

  name: str
  register_service: Callable[[Server], None] = field(init = False)
  add_service_to_server: InitVar[Callable[[Service, Server], None]]
  service: InitVar[Service]

  def __post_init__(
      self,
      add_service_to_server: Callable[[Service, Server], None],
      service: Service) -> None :

    def register_service(server: Server) -> None:
      """Register the service to the server."""
      add_service_to_server(service, server)  # pragma: no cover

    self.register_service = register_service
