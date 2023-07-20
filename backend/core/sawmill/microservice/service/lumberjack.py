"""Lumberjack service."""

# Python.
from typing import Callable, cast

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.proto.core_pb2 import ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import (
  DESCRIPTOR,
  ErrorRequest,
  EventRequest,
  GrpcRequestRequest,
  HttpRequestRequest,
  ResponseRequest,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
    LumberjackServicer as Servicer,
    add_LumberjackServicer_to_server as addToServer
)
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
      return SINGLETON.structuredLogger.sendLogHttpRequest(grpc = request)  # type: ignore[return-value]  # pylint: disable=line-too-long
    return self._handleLogging(method = method)

  def LogHttpRequestResponse(
      self,
      request: ResponseRequest,
      _      : grpc.ServicerContext,
  ) -> ObjectMetadata :
    """Log HTTP request responses."""
    def method() -> ResponseMetadataMixin :
      LOGGER.info(
        f'Saving the response to the HTTP request "{request.requestMetadata.httpCaller.requestId}" '
        'to the database.',
      )
      return SINGLETON.structuredLogger.sendLogHttpResponse(grpc = request)  # type: ignore[return-value]  # pylint: disable=line-too-long
    return self._handleResponse(method = method)

  def LogGrpcRequest(
      self,
      request: GrpcRequestRequest,
      _      : grpc.ServicerContext,
  ) -> ObjectMetadata :
    """Log requests."""
    def method() -> MetadataMixin :
      LOGGER.info(
        f'Saving the gRPC request "{request.requestMetadata.grpcCaller.requestId}" '
        'to the database.',
      )
      return SINGLETON.structuredLogger.sendLogGrpcRequest(grpc = request)  # type: ignore[return-value]  # pylint: disable=line-too-long
    return self._handleLogging(method = method)

  def LogGrpcResponse(
      self,
      request: ResponseRequest,
      _      : grpc.ServicerContext,
  ) -> ObjectMetadata :
    """Log request responses."""
    def method() -> ResponseMetadataMixin :
      LOGGER.info(
        f'Saving the response to the gRPC request "{request.requestMetadata.grpcCaller.requestId}" '
        'to the database.',
      )
      return SINGLETON.structuredLogger.sendLogGrpcResponse(grpc = request)  # type: ignore[return-value]  # pylint: disable=line-too-long
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
      return SINGLETON.structuredLogger.sendLogEvent(grpc = request)  # type: ignore[return-value]  # pylint: disable=line-too-long
    return self._handleLogging(method = method)

  def LogError(self, request: ErrorRequest, _: grpc.ServicerContext) -> ObjectMetadata :
    """Log errors."""
    def method() -> MetadataMixin :
      LOGGER.info(
        f'Saving an error to the request "{request.requestMetadata.grpcCaller.requestId}" '
        'to the database.',
      )
      return SINGLETON.structuredLogger.sendLogError(grpc = request)  # type: ignore[return-value]  # pylint: disable=line-too-long
    return self._handleLogging(method = method)


  def _handleLogging(self, *, method: Callable[[], MetadataMixin]) -> ObjectMetadata :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.metaLoggingErrors:
      raise InvalidArgumentException(
        privateMessage = 'Error when parsing the metadata fields.',
        privateDetails = metadata.metaLoggingErrors,
      )
    return cast(ObjectMetadata, metadata.toObjectMetadata())


  def _handleResponse(self, *, method: Callable[[], ResponseMetadataMixin]) -> ObjectMetadata :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.metaResponseLoggingErrors:
      raise InvalidArgumentException(
        privateMessage = 'Error when parsing the metadata fields.',
        privateDetails = metadata.metaResponseLoggingErrors,
      )
    return cast(ObjectMetadata, metadata.toObjectMetadata())


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
