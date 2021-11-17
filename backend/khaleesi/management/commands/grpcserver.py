"""Command to start the gRPC server."""

# Python.
from concurrent import futures
from typing import Any, cast

# Django.
from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from django.utils.module_loading import import_string

# gRPC.
import grpc
from grpc_reflection.v1alpha import reflection

# khaleesi.ninja.
from khaleesi.core.settings import KhaleesiNinjaSettings


khaleesi_settings = cast(KhaleesiNinjaSettings, settings.KHALEESI_NINJA)


class Command(BaseCommand):
  """Command to start the gRPC server."""
  help = 'Starts the gRPC server.'

  def add_arguments(self, parser: CommandParser) -> None :
    parser.add_argument(
      'address', nargs = '?', default = f'[::]:{khaleesi_settings["PORT"]}',
      help = 'Optional address for which to open a port.'
    )
    parser.add_argument(
      '--max-workers', type = int, default = 10, dest = 'max_workers',
      help = 'Number of maximum worker threads.'
    )

  def handle(self, *args: Any, **options: Any) -> None :
    self.run(**options)

  def run(self, **options: Any) -> None :
    """Run the server."""
    self._serve(**options)

  def _serve(self, **options: Any) -> None :
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = options['max_workers']))
    self._add_handlers(server)
    server.add_insecure_port(options['address'])
    self.stdout.write(f'Starting gRPC server at {options["address"]}...')
    server.start()
    server.wait_for_termination()

  @staticmethod
  def _add_handlers(server: grpc.Server) -> None :
    """
    Attempt to import a class from a string representation.
    """
    raw_handlers = khaleesi_settings["GRPC_HANDLERS"]
    service_names = [reflection.SERVICE_NAME]
    for raw_handler in raw_handlers:
      handler = f'{raw_handler}.service_configuration'
      try:
        name, register_handler = import_string(handler)
        register_handler(server)
        if settings.DEBUG:
          service_names.append(name)
      except ImportError as error:
        raise ImportError(f'Could not import "{handler}" for gRPC handler.') from error
    if settings.DEBUG:
      reflection.enable_server_reflection(service_names, server)
