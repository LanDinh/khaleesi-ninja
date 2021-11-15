"""Command to start the gRPC server."""

# Python.
from concurrent import futures

# Django.
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string

# gRPC.
import grpc
from grpc_reflection.v1alpha import reflection


class Command(BaseCommand):
  """Command to start the gRPC server."""
  help = 'Starts the gRPC server.'

  def add_arguments(self, parser):
    parser.add_argument(
      'address', nargs = '?', default = f'[::]:{settings.KHALEESI_NINJA["PORT"]}',
      help = 'Optional address for which to open a port.'
    )
    parser.add_argument(
      '--max-workers', type = int, default = 10, dest = 'max_workers',
      help = 'Number of maximum worker threads.'
    )

  def handle(self, *args, **options):
    self.run(**options)

  def run(self, **options):
    """Run the server."""
    self._serve(**options)

  def _serve(self, **options):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = options['max_workers']))
    self._add_handlers(server)
    server.add_insecure_port(options['address'])
    self.stdout.write(f'Starting gRPC server at {options["address"]}...')
    server.start()
    server.wait_for_termination()

  @staticmethod
  def _add_handlers(server):
    """
    Attempt to import a class from a string representation.
    """
    raw_handlers = settings.KHALEESI_NINJA["GRPC_HANDLERS"]
    service_names = [reflection.SERVICE_NAME]
    for raw_handler in raw_handlers:
      handler = f'{raw_handler}.service_configuration'
      try:
        name, register_handler = import_string(handler)
        register_handler(server)
        if settings.DEBUG:
          service_names.append(name)
      except ImportError as e:
        raise ImportError(f'Could not import "{handler}" for gRPC handler.')
    if settings.DEBUG:
      reflection.enable_server_reflection(service_names, server)
