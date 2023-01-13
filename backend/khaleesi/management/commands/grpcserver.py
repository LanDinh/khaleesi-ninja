"""Command to start the gRPC server."""

# Python.
from typing import Any, Callable
from uuid import uuid4

# Django.
from django.conf import settings
from django.core.management.commands.migrate import Command as DjangoMigrateCommand

# gRPC.
from grpc import StatusCode

# Prometheus.
from prometheus_client import start_http_server

# khaleesi.ninja.
from khaleesi.core.grpc.server import Server
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.management.commands._base import BaseCommand


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Command(BaseCommand, DjangoMigrateCommand):
  """Command to start the gRPC server."""

  help = 'Starts the gRPC server.'
  server_start_backgate_request_id: str
  server                          : Server

  def khaleesi_handle(self, *args: Any, **options: Any) -> None :
    """Start the gRPC server."""
    # Starting server start.
    self.server_start_backgate_request_id = str(uuid4())
    try:
      if khaleesi_settings['STARTUP']['MIGRATIONS_BEFORE_SERVER_START']['REQUIRED']:
        options_copy = options.copy()
        options_copy['database']  = 'migrate'
        options_copy['app_label'] = 'microservice'
        options_copy['migration_name'] = \
          khaleesi_settings['STARTUP']['MIGRATIONS_BEFORE_SERVER_START']['MIGRATION']
        DjangoMigrateCommand.handle(self, *args, **options_copy)

      SINGLETON.structured_logger.log_system_backgate_request(
        backgate_request_id = self.server_start_backgate_request_id,
        grpc_method         = 'LIFECYCLE',
      )

      self._log_system_request(**options, method = self._migrate   , grpc_method = 'MIGRATE')
      self._log_system_request(**options, method = self._initialize, grpc_method = 'INITIALIZE')
      self._log_system_request(**options, method = self._start     , grpc_method = 'LIFECYCLE')

      SINGLETON.structured_logger.log_system_backgate_response(
        backgate_request_id = self.server_start_backgate_request_id,
        grpc_method         = 'LIFECYCLE',
        status              = StatusCode.OK,
      )

      self.server.wait_for_termination()
    except KhaleesiException as exception:
      SINGLETON.structured_logger.log_system_backgate_response(
        backgate_request_id = self.server_start_backgate_request_id,
        grpc_method         = 'LIFECYCLE',
        status              = exception.status,
      )
      raise
    except Exception:
      SINGLETON.structured_logger.log_system_backgate_response(
        backgate_request_id = self.server_start_backgate_request_id,
        grpc_method         = 'LIFECYCLE',
        status              = StatusCode.INTERNAL,
      )
      raise

  # noinspection PyUnusedLocal
  def _migrate(self, request_id: str, **options: Any) -> None :  # pylint: disable=unused-argument
    """Perform migration."""
    options_copy = options.copy()
    options_copy['database']  = 'migrate'
    options_copy['app_label'] = 'microservice'
    DjangoMigrateCommand.handle(self, **options_copy)

  # noinspection PyUnusedLocal
  def _initialize(self, request_id: str, **options: Any) -> None :  # pylint: disable=unused-argument
    """Initialize the server."""
    self.server = Server(
      start_backgate_request_id = self.server_start_backgate_request_id,
      initialize_request_id     = request_id,
    )

  # noinspection PyUnusedLocal
  def _start(self, request_id: str, **options: Any) -> None :  # pylint: disable=unused-argument
    """Start the server."""
    start_http_server(int(khaleesi_settings['MONITORING']['PORT']))
    self.server.start(start_request_id = request_id)

  def _log_system_request(self, *, method: Callable, grpc_method: str, **options: Any) -> None :  # type: ignore[type-arg]  # pylint: disable=line-too-long
    """Log the passed method as system request."""
    request_id = str(uuid4())
    SINGLETON.structured_logger.log_system_request(
      backgate_request_id = self.server_start_backgate_request_id,
      request_id          = request_id,
      grpc_method         = grpc_method,
    )
    try:
      method(request_id = request_id, **options)
      SINGLETON.structured_logger.log_system_response(
        backgate_request_id = self.server_start_backgate_request_id,
        request_id          = request_id,
        grpc_method         = grpc_method,
        status              = StatusCode.OK,
      )
    except KhaleesiException as exception:
      self._log_exception(
        exception   = exception,
        request_id  = request_id,
        grpc_method = grpc_method
      )
      raise
    except Exception as exception:
      khaleesi_exception = MaskingInternalServerException(exception = exception)
      self._log_exception(
        exception   = khaleesi_exception,
        request_id  = request_id,
        grpc_method = grpc_method
      )
      raise khaleesi_exception from exception

  def _log_exception(
      self, *,
      exception: KhaleesiException,
      request_id: str,
      grpc_method: str,
  ) -> None :
    SINGLETON.structured_logger.log_system_error(
      exception           = exception,
      backgate_request_id = self.server_start_backgate_request_id,
      request_id          = request_id,
      grpc_method         = grpc_method,
    )
    SINGLETON.structured_logger.log_system_response(
      backgate_request_id = self.server_start_backgate_request_id,
      request_id          = request_id,
      grpc_method         = grpc_method,
      status              = exception.status,
    )
