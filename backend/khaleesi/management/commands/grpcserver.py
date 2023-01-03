"""Command to start the gRPC server."""

# Python.
from typing import Any

# Django.
from django.conf import settings

# Prometheus.
from prometheus_client import start_http_server

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.management.commands._base import BaseCommand


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Command(BaseCommand):
  """Command to start the gRPC server."""

  help = 'Starts the gRPC server.'

  def khaleesi_handle(self, *args: Any, **options: Any) -> None :
    """Start the gRPC server."""
    server = Server()
    start_http_server(int(khaleesi_settings['MONITORING']['PORT']))
    server.start()
