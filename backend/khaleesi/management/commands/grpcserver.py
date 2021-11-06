"""Command to start the gRPC server."""

# Python.
from concurrent import futures

# Django.
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string

# gRPC.
import grpc


class Command(BaseCommand):
  """Command to start the gRPC server."""
  help = 'Starts the gRPC server.'

  def add_arguments(self, parser):
    parser.add_argument(
      'address', nargs = '?', default = '[::]:50051',
      help = 'Optional address for which to open a port.'
    )
    parser.add_argument(
      '--max-workers', type = int, default = 10, dest = 'max_workers',
      help = 'Number of maximum worker threads.'
    )

  def handle(self, *args, **options):
    self.address = options['address']
    self.max_workers = options['max_workers']
    self.run(**options)

  def run(self, **options):
    """Run the server."""
    self.stdout.write(f'Starting gRPC server at ${self.address}')
    self._serve()

  def _serve(self):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = self.max_workers))
    self._import_handler(server)
    server.add_insecure_port(self.address)
    server.start()
    server.wait_for_termination()

  @staticmethod
  def _import_handler(server):
    """
    Attempt to import a class from a string representation.
    """
    value = f'{settings.GRPC_HANDLER}.register_handler'
    try:
      import_string(value)(server)
    except ImportError as e:
      raise ImportError(f'Could not import "${value}" for gRPC handler.')
