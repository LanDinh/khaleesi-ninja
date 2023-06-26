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


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Command(BaseCommand, DjangoMigrateCommand):
  """Command to start the gRPC server."""

  help = 'Starts the gRPC server.'
  serverStartHttpRequestId: str
  server                  : Server

  def khaleesiHandle(self, *args: Any, **options: Any) -> None :
    """Start the gRPC server."""
    # Starting server start.
    self.serverStartHttpRequestId = str(uuid4())
    try:
      if khaleesiSettings['STARTUP']['MIGRATIONS_BEFORE_SERVER_START']['REQUIRED']:
        optionsCopy = options.copy()
        optionsCopy['database']  = 'migrate'
        optionsCopy['app_label'] = 'microservice'
        optionsCopy['migration_name'] = \
          khaleesiSettings['STARTUP']['MIGRATIONS_BEFORE_SERVER_START']['MIGRATION']
        DjangoMigrateCommand.handle(self, *args, **optionsCopy)

      SINGLETON.structuredLogger.logSystemHttpRequest(
        httpRequestId = self.serverStartHttpRequestId,
        grpcMethod    = 'LIFECYCLE',
      )

      self._logSystemRequest(**options, method = self._migrate   , grpcMethod = 'MIGRATE')
      self._logSystemRequest(**options, method = self._initialize, grpcMethod = 'INITIALIZE')
      self._logSystemRequest(**options, method = self._start     , grpcMethod = 'LIFECYCLE')

      SINGLETON.structuredLogger.logSystemHttpResponse(
        httpRequestId = self.serverStartHttpRequestId,
        grpcMethod    = 'LIFECYCLE',
        status        = StatusCode.OK,
      )

      self.server.waitForTermination()
    except KhaleesiException as exception:
      SINGLETON.structuredLogger.logSystemHttpResponse(
        httpRequestId = self.serverStartHttpRequestId,
        grpcMethod    = 'LIFECYCLE',
        status        = exception.status,
      )
      raise
    except Exception:
      SINGLETON.structuredLogger.logSystemHttpResponse(
        httpRequestId = self.serverStartHttpRequestId,
        grpcMethod    = 'LIFECYCLE',
        status        = StatusCode.INTERNAL,
      )
      raise

  # noinspection PyUnusedLocal
  def _migrate(self, grpcRequestId: str, **options: Any) -> None :  # pylint: disable=unused-argument
    """Perform migration."""
    optionsCopy = options.copy()
    optionsCopy['database']  = 'migrate'
    optionsCopy['app_label'] = 'microservice'
    DjangoMigrateCommand.handle(self, **optionsCopy)
    optionsCopy['app_label'] = 'khaleesi'
    DjangoMigrateCommand.handle(self, **optionsCopy)

  # noinspection PyUnusedLocal
  def _initialize(self, grpcRequestId: str, **options: Any) -> None :  # pylint: disable=unused-argument
    """Initialize the server."""
    self.server = Server(
      startHttpRequestId      = self.serverStartHttpRequestId,
      initializeGrpcRequestId = grpcRequestId,
    )

  # noinspection PyUnusedLocal
  def _start(self, grpcRequestId: str, **options: Any) -> None :  # pylint: disable=unused-argument
    """Start the server."""
    start_http_server(int(khaleesiSettings['MONITORING']['PORT']))
    self.server.start(startGrpcRequestId = grpcRequestId)

  def _logSystemRequest(self, *, method: Callable, grpcMethod: str, **options: Any) -> None :  # type: ignore[type-arg]  # pylint: disable=line-too-long
    """Log the passed method as system request."""
    grpcRequestId = str(uuid4())
    SINGLETON.structuredLogger.logSystemGrpcRequest(
      httpRequestId = self.serverStartHttpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )
    try:
      method(grpcRequestId = grpcRequestId, **options)
      SINGLETON.structuredLogger.logSystemGrpcResponse(
        httpRequestId = self.serverStartHttpRequestId,
        grpcRequestId = grpcRequestId,
        grpcMethod    = grpcMethod,
        status        = StatusCode.OK,
      )
    except KhaleesiException as exception:
      self._logException(
        exception     = exception,
        grpcRequestId = grpcRequestId,
        grpcMethod    = grpcMethod,
      )
      raise
    except Exception as exception:
      khaleesiException = MaskingInternalServerException(exception = exception)
      self._logException(
        exception     = khaleesiException,
        grpcRequestId = grpcRequestId,
        grpcMethod    = grpcMethod,
      )
      raise khaleesiException from exception

  def _logException(self, *,
      exception    : KhaleesiException,
      grpcRequestId: str,
      grpcMethod   : str,
  ) -> None :
    SINGLETON.structuredLogger.logSystemError(
      exception     = exception,
      httpRequestId = self.serverStartHttpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )
    SINGLETON.structuredLogger.logSystemGrpcResponse(
      httpRequestId = self.serverStartHttpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
      status        = exception.status,
    )
