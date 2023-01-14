"""Lumberjack service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import (
  DESCRIPTOR,
  LogStandardResponse,
  EmptyRequest,
  Error,
  Event,
  ResponseRequest,
  Request,
  BackgateRequest,
  BackgateResponseRequest,
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
  Query as DbQuery,
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
      LOGGER.info(
        f'Saving an event to the request "{request.request_metadata.caller.request_id}" '
        f'to the database.',
      )
      return DbEvent.objects.log_event(grpc_event = request)

    return self._handle_response(method = method)

  def LogBackgateRequest(
      self,
      request: BackgateRequest,
      _: grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log backgate request."""
    def method() -> Metadata :
      LOGGER.info(
        f'Saving the backgate request "{request.request_metadata.caller.backgate_request_id}" '
        'to the database.',
      )
      return DbBackgateRequest.objects.log_backgate_request(grpc_backgate_request = request)
    return self._handle_response(method = method)

  def LogSystemBackgateRequest(
      self,
      request: EmptyRequest,
      _: grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log backgate request."""
    def method() -> Metadata :
      LOGGER.info(
        'Saving the system backgate request '
        f'"{request.request_metadata.caller.backgate_request_id}" to the database.',
      )
      return DbBackgateRequest.objects.log_system_backgate_request(grpc_backgate_request = request)
    return self._handle_response(method = method)

  def LogBackgateRequestResponse(
      self,
      request: BackgateResponseRequest,
      _: grpc.ServicerContext,
  ) -> LogStandardResponse :
    """Log request responses."""
    def method() -> Metadata :
      LOGGER.info(
        'Saving the response to the backgate request '
        f'"{request.request_metadata.caller.backgate_request_id}" to the database.',
      )
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
      LOGGER.info(
        f'Saving the request "{request.request_metadata.caller.request_id}" to the database.',
      )
      return DbRequest.objects.log_request(grpc_request = request)

    return self._handle_response(method = method)

  def LogResponse(self, request: ResponseRequest, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log request responses."""
    def method() -> Metadata :
      LOGGER.info(
        f'Saving the response to the request "{request.request_metadata.caller.request_id}" '
        f'to the database.',
      )
      result = DbRequest.objects.log_response(grpc_response = request)
      DbBackgateRequest.objects.add_child_duration(request = result)
      LOGGER.info('Saving the queries to the database.')
      queries = DbQuery.objects.log_queries(
        queries = request.queries,
        metadata = result.to_grpc_request_response().request.request_metadata,
      )
      errors = result.meta_logging_errors
      LOGGER.info('Processing the query times and errors.')
      for query in queries:
        errors += query.meta_logging_errors
        result.meta_child_duration += query.reported_duration
      result.save()
      result.meta_logging_errors = errors
      return result
    return self._handle_response(method = method)

  def LogError(self, request: Error, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log errors."""
    def method() -> Metadata :
      LOGGER.info(
        f'Saving an error to the request "{request.request_metadata.caller.request_id}" '
        'to the database.',
      )
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
