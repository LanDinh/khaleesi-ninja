"""Lumberjack service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.proto.core_pb2 import EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import (
  DESCRIPTOR,
  LogStandardResponse,
  Error,
  Event,
  GrpcResponseRequest,
  GrpcRequest,
  HttpRequest,
  HttpResponseRequest,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
    LumberjackServicer as Servicer,
    add_LumberjackServicer_to_server as addToServer
)
from microservice.models import (
  Event as DbEvent,
  GrpcRequest as DbGrpcRequest,
  Error as DbError,
  HttpRequest as DbHttpRequest,
  Query as DbQuery,
)
from microservice.models.logs.abstract import Metadata
from microservice.models.serviceRegistry import SERVICE_REGISTRY


class Service(Servicer):
  """Lumberjack service."""

  def LogEvent(self, request: Event, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log events."""
    def method() -> Metadata :
      LOGGER.info('Adding service to service registry.')
      SERVICE_REGISTRY.addService(callerDetails = request.requestMetadata.caller)
      LOGGER.info(
        f'Saving an event to the request "{request.requestMetadata.caller.grpcRequestId}" '
        f'to the database.',
      )
      return DbEvent.objects.logEvent(grpcEvent = request)

    return self._handleResponse(method = method)

  def LogHttpRequest(self, request: HttpRequest, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log HTTP request."""
    def method() -> Metadata :
      LOGGER.info(
        f'Saving the HTTP request "{request.requestMetadata.caller.httpRequestId}" '
        'to the database.',
      )
      return DbHttpRequest.objects.logRequest(grpcRequest = request)
    return self._handleResponse(method = method)

  def LogSystemHttpRequest(
      self,
      request: EmptyRequest,
      _      : grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log HTTP request."""
    def method() -> Metadata :
      LOGGER.info(
        'Saving the system HTTP request '
        f'"{request.requestMetadata.caller.httpRequestId}" to the database.',
      )
      return DbHttpRequest.objects.logSystemRequest(grpcRequest = request)
    return self._handleResponse(method = method)

  def LogHttpRequestResponse(
      self,
      request: HttpResponseRequest,
      _      : grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log HTTP request responses."""
    def method() -> Metadata :
      LOGGER.info(
        'Saving the response to the HTTP request '
        f'"{request.requestMetadata.caller.httpRequestId}" to the database.',
      )
      return DbHttpRequest.objects.logResponse(grpcResponse = request)
    return self._handleResponse(method = method)

  def LogGrpcRequest(self, request: GrpcRequest, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log requests."""
    def method() -> Metadata :
      LOGGER.info('Adding call to service registry.')
      SERVICE_REGISTRY.addCall(
        callerDetails = request.upstreamRequest,
        calledDetails = request.requestMetadata.caller,
      )
      LOGGER.info(
        f'Saving the request "{request.requestMetadata.caller.grpcRequestId}" to the database.',
      )
      return DbGrpcRequest.objects.logRequest(grpcRequest = request)

    return self._handleResponse(method = method)

  def LogGrpcResponse(
      self,
      request: GrpcResponseRequest,
      _      : grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log request responses."""
    def method() -> Metadata :
      LOGGER.info(
        f'Saving the response to the request "{request.requestMetadata.caller.grpcRequestId}" '
        f'to the database.',
      )
      result = DbGrpcRequest.objects.logResponse(grpcResponse = request)
      try:
        DbHttpRequest.objects.addChildDuration(request = result)
      except Exception:  # pylint: disable=broad-except  # pragma: no cover
        # TODO(45) - remove this hack
        pass
      LOGGER.info('Saving the queries to the database.')
      queries = DbQuery.objects.logQueries(
        queries  = request.queries,
        metadata = result.toGrpc().request.requestMetadata,
      )
      errors = result.metaLoggingErrors
      LOGGER.info('Processing the query times and errors.')
      for query in queries:
        errors += query.metaLoggingErrors
        result.metaChildDuration += query.reportedDuration
      result.save()
      result.metaLoggingErrors = errors
      return result
    return self._handleResponse(method = method)

  def LogError(self, request: Error, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log errors."""
    def method() -> Metadata :
      LOGGER.info(
        f'Saving an error to the request "{request.requestMetadata.caller.grpcRequestId}" '
        'to the database.',
      )
      return DbError.objects.logError(grpcError = request)
    return self._handleResponse(method = method)


  def _handleResponse(self, *, method: Callable[[], Metadata]) -> LogStandardResponse :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.metaLoggingErrors:
      raise InvalidArgumentException(
        privateMessage = 'Error when parsing the metadata fields.',
        privateDetails = metadata.metaLoggingErrors,
      )
    return LogStandardResponse()


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
