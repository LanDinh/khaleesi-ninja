"""Lumberjack service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.proto.core_pb2 import ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import (
  DESCRIPTOR,
  LogStandardResponse,
  ErrorRequest,
  EventRequest,
  GrpcResponseRequest,
  GrpcRequest,
  HttpRequestRequest,
  ResponseRequest,
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
from microservice.models.logs.metadataMixin import MetadataMixin
from microservice.models.logs.responseMetadataMixin import ResponseMetadataMixin
from microservice.models.serviceRegistry import SERVICE_REGISTRY


class Service(Servicer):
  """Lumberjack service."""

  def LogHttpRequest(
      self,
      request: HttpRequestRequest,
      _      : grpc.ServicerContext,
  ) -> ObjectMetadata :
    """Log HTTP request."""
    def method() -> MetadataMixin :
      LOGGER.info(
        f'Saving the HTTP request "{request.requestMetadata.httpCaller.requestId}" '
        'to the database.',
      )
      dbHttpRequest = DbHttpRequest()
      dbHttpRequest.khaleesiSave(grpc = request)
      return dbHttpRequest
    return self._handleLogging(method = method)

  def LogHttpRequestResponse(
      self,
      request: ResponseRequest,
      _      : grpc.ServicerContext,
  ) -> ObjectMetadata :
    """Log HTTP request responses."""
    requestId = request.requestMetadata.httpCaller.requestId
    def method() -> ResponseMetadataMixin :
      LOGGER.info(
        f'Saving the response to the HTTP request "{requestId}" to the database.',
      )
      dbHttpRequest = DbHttpRequest.objects.get(metaCallerHttpRequestId = requestId)
      dbHttpRequest.finish(request = request)
      return dbHttpRequest
    return self._handleResponse(method = method)

  def LogEvent(self, request: EventRequest, _: grpc.ServicerContext) -> ObjectMetadata :
    """Log events."""
    def method() -> MetadataMixin :
      LOGGER.info('Adding service to service registry.')
      SERVICE_REGISTRY.addService(callerDetails = request.requestMetadata.grpcCaller)
      LOGGER.info(
        f'Saving an event to the request "{request.requestMetadata.grpcCaller.requestId}" '
        f'to the database.',
      )
      dbEvent = DbEvent()
      dbEvent.khaleesiSave(grpc = request)
      return dbEvent
    return self._handleLogging(method = method)

  def LogError(self, request: ErrorRequest, _: grpc.ServicerContext) -> ObjectMetadata :
    """Log errors."""
    def method() -> MetadataMixin :
      LOGGER.info(
        f'Saving an error to the request "{request.requestMetadata.grpcCaller.requestId}" '
        'to the database.',
      )
      dbError = DbError()
      dbError.khaleesiSave(grpc = request)
      return dbError
    return self._handleLogging(method = method)

  def LogGrpcRequest(self, request: GrpcRequest, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log requests."""
    def method() -> Metadata :
      LOGGER.info('Adding call to service registry.')
      SERVICE_REGISTRY.addCall(
        callerDetails = request.upstreamRequest,
        calledDetails = request.requestMetadata.grpcCaller,
      )
      LOGGER.info(
        f'Saving the request "{request.requestMetadata.grpcCaller.requestId}" to the database.',
      )
      return DbGrpcRequest.objects.logRequest(grpcRequest = request)

    return self._handleResponseOld(method = method)

  def LogGrpcResponse(
      self,
      request: GrpcResponseRequest,
      _      : grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log request responses."""
    def method() -> Metadata :
      LOGGER.info(
        f'Saving the response to the request "{request.requestMetadata.grpcCaller.requestId}" '
        f'to the database.',
      )
      result = DbGrpcRequest.objects.logResponse(grpcResponse = request)
      try:
        dbHttpRequest = DbHttpRequest.objects.get(
          metaCallerHttpRequestId = request.requestMetadata.httpCaller.requestId,
        )
        dbHttpRequest.addChildDuration(request = result)
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
    return self._handleResponseOld(method = method)


  def _handleResponseOld(self, *, method: Callable[[], Metadata]) -> LogStandardResponse :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.metaLoggingErrors:
      raise InvalidArgumentException(
        privateMessage = 'Error when parsing the metadata fields.',
        privateDetails = metadata.metaLoggingErrors,
      )
    return LogStandardResponse()


  def _handleLogging(self, *, method: Callable[[], MetadataMixin]) -> ObjectMetadata :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.metaLoggingErrors:
      raise InvalidArgumentException(
        privateMessage = 'Error when parsing the metadata fields.',
        privateDetails = metadata.metaLoggingErrors,
      )
    return metadata.toObjectMetadata()


  def _handleResponse(self, *, method: Callable[[], ResponseMetadataMixin]) -> ObjectMetadata :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.metaResponseLoggingErrors:
      raise InvalidArgumentException(
        privateMessage = 'Error when parsing the metadata fields.',
        privateDetails = metadata.metaResponseLoggingErrors,
      )
    return metadata.toObjectMetadata()


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
