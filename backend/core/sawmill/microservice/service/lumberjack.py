"""Lumberjack service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import (
    DESCRIPTOR,
    Error, Event, ResponseRequest,
    Request, LogRequestResponse,
    LogStandardResponse,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
    LumberjackServicer as Servicer,
    add_LumberjackServicer_to_server as add_to_server
)
from microservice.models import Event as DbEvent, Request as DbRequest, Error as DbError
from microservice.models.abstract import Metadata
from microservice.models.service_registry import SERVICE_REGISTRY


class Service(Servicer):
  """Lumberjack service."""

  def LogEvent(self, request: Event, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log events."""
    def method() -> Metadata :
      result = DbEvent.objects.log_event(grpc_event = request)
      SERVICE_REGISTRY.add_service(caller_details = request.request_metadata.caller)
      return result

    self._handle_response(method = method)
    return LogStandardResponse()

  def LogRequest(self, request: Request, _: grpc.ServicerContext) -> LogRequestResponse :
    """Log requests."""
    def method() -> Metadata:
      result = DbRequest.objects.log_request(grpc_request = request)
      SERVICE_REGISTRY.add_call(
        caller_details = request.upstream_request,
        called_details = request.request_metadata.caller,
      )
      return result

    logged_request = self._handle_response(method = method)
    response = LogRequestResponse()
    response.request_id = logged_request.pk
    return response

  def LogResponse(self, request: ResponseRequest, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log request responses."""
    self._handle_response(method = lambda: DbRequest.objects.log_response(grpc_response = request))
    return LogStandardResponse()

  def LogError(self, request: Error, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log errors."""
    self._handle_response(method = lambda: DbError.objects.log_error(grpc_error = request))
    return LogStandardResponse()


  def _handle_response(self, *, method: Callable[[], Metadata]) -> Metadata :
    """Wrap responses for logging."""
    metadata = method()
    if metadata.meta_logging_errors:
      raise InvalidArgumentException(
        private_message = 'Error when parsing the metadata fields.',
        private_details = metadata.meta_logging_errors,
      )
    return metadata


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
