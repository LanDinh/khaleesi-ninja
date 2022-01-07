"""Command to start the gRPC server."""

# Python.
from concurrent import futures
from signal import signal, SIGTERM
from typing import Any

# Django.
from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from django.utils.module_loading import import_string

# gRPC.
import grpc
from grpc_reflection.v1alpha import reflection

# prometheus.
# noinspection PyProtectedMember
from prometheus_client import start_http_server  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long

# khaleesi.ninja.
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.metrics import HEALTH as HEALTH_METRIC
from khaleesi.core.settings.definition import KhaleesiNinjaSettings


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


class Command(BaseCommand):
  """Command to start the gRPC server."""
  help = 'Starts the gRPC server.'

  def add_arguments(self, parser: CommandParser) -> None :
    parser.add_argument(
      'address', nargs = '?', default = f'[::]:{khaleesi_settings["GRPC"]["PORT"]}',
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
    interceptors = [ PrometheusServerInterceptor() ]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers = options['max_workers']),
        interceptors = interceptors  # type: ignore[arg-type] # fixed upstream
    )
    self._add_handlers(server)
    server.add_insecure_port(options['address'])
    self.stdout.write(f'Starting gRPC server at {options["address"]}...')
    server.start()
    start_http_server(int(khaleesi_settings['MONITORING']['PORT']))

    def handle_sigterm(*_: Any) -> None :
      """Shutdown gracefully."""
      self.stdout.write(f'Stopping gRPC server at {options["address"]}...')
      HEALTH_METRIC.set_terminating()
      done_event = server.stop(30)
      done_event.wait(30)
      self.stdout.write('Stop complete.')

    signal(SIGTERM, handle_sigterm)
    server.wait_for_termination()

  @staticmethod
  def _add_handlers(server: grpc.Server) -> None :
    """
    Attempt to import a class from a string representation.
    """
    raw_handlers = khaleesi_settings['GRPC']['HANDLERS']
    service_names = [reflection.SERVICE_NAME]
    for raw_handler in raw_handlers:
      handler = f'{raw_handler}.service_configuration'
      try:
        service_configuration = import_string(handler)
        service_configuration.register_service(server)
        service_names.append(service_configuration.name)
      except ImportError as error:
        raise ImportError(f'Could not import "{handler}" for gRPC handler.') from error
    reflection.enable_server_reflection(service_names, server)
