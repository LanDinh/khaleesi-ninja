"""Lumberjack service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.shared.logger import LOGGER
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import (
    DESCRIPTOR, LogStandardResponse, EmptyRequest,
    Error, Event, ResponseRequest, Request, BackgateRequest,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
    LumberjackServicer as Servicer,
    add_LumberjackServicer_to_server as add_to_server
)
from microservice.models import (
  Event as DbEvent,
  Request as DbRequest,
  Error as DbError,
  BackgateRequest as DbBackgateRequest,
)
from microservice.models.logs.abstract import Metadata
from microservice.models.service_registry import SERVICE_REGISTRY


class Service(Servicer):
  """Lumberjack service."""

  def LogEvent(self, request: Event, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log events."""
    def method() -> Metadata :
      LOGGER.info('Adding service to service registry.')
      SERVICE_REGISTRY.add_service(caller_details = request.request_metadata.caller)
      LOGGER.info('Saving the event to the database.')
      return DbEvent.objects.log_event(grpc_event = request)

    return self._handle_response(method = method)

  def LogBackgateRequest(
      self,
      request: BackgateRequest,
      _: grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log backgate request."""
    def method() -> Metadata :
      LOGGER.info('Saving the backgate request to the database.')
      return DbBackgateRequest.objects.log_backgate_request(grpc_backgate_request = request)
    return self._handle_response(method = method)

  def LogSystemBackgateRequest(
      self,
      request: EmptyRequest,
      _: grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log backgate request."""
    def method() -> Metadata :
      LOGGER.info('Saving the backgate request to the database.')
      return DbBackgateRequest.objects.log_system_backgate_request(grpc_backgate_request = request)
    return self._handle_response(method = method)

  def LogBackgateRequestResponse(
      self,
      request: ResponseRequest,
      _: grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log request responses."""
    def method() -> Metadata :
      LOGGER.info('Saving the backgate response to the database.')
      return DbBackgateRequest.objects.log_response(grpc_response = request)
    return self._handle_response(method = method)

  def LogRequest(self, request: Request, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log requests."""
    def method() -> Metadata :
      LOGGER.info('Adding call to service registry.')
      SERVICE_REGISTRY.add_call(
        caller_details = request.upstream_request,
        called_details = request.request_metadata.caller,
      )
      LOGGER.info('Saving the request to the database.')
      return DbRequest.objects.log_request(grpc_request = request)

    return self._handle_response(method = method)

  def LogResponse(self, request: ResponseRequest, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log request responses."""
    def method() -> Metadata :
      LOGGER.info('Saving the response to the database.')
      return DbRequest.objects.log_response(grpc_response = request)
    return self._handle_response(method = method)

  def LogError(self, request: Error, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log errors."""
    def method() -> Metadata :
      LOGGER.info('Saving the error to the database.')
      return DbError.objects.log_error(grpc_error = request)
    return self._handle_response(method = method)


  def _handle_response(self, *, method: Callable[[], Metadata]) -> LogStandardResponse :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.meta_logging_errors:
      raise InvalidArgumentException(
        private_message = 'Error when parsing the metadata fields.',
        private_details = metadata.meta_logging_errors,
      )
    return LogStandardResponse()


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
