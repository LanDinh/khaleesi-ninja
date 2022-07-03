"""core-sawmill service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.shared.exceptions import (
    KhaleesiException,
    InvalidArgumentException,
    InternalServerException,
)
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import (
    DESCRIPTOR,
    Event, ResponseRequest,
    Request, LogRequestResponse,
    LogStandardResponse,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
    LumberjackServicer as Servicer,
    add_LumberjackServicer_to_server as add_to_server
)
from microservice.models import Event as DbEvent, Request as DbRequest
from microservice.models.abstract import Metadata
from microservice.models.service_registry import SERVICE_REGISTRY


class Service(Servicer):
  """core-sawmill service."""

  def LogEvent(self, request: Event, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log events."""
    def method() -> Metadata :
      SERVICE_REGISTRY.add(caller_details = request.request_metadata.caller)
      return DbEvent.objects.log_event(grpc_event = request)

    self._handle_response(method = method)
    return LogStandardResponse()

  def LogRequest(self, request: Request, _: grpc.ServicerContext) -> LogRequestResponse :
    """Log requests."""
    def method() -> Metadata:
      SERVICE_REGISTRY.add(caller_details = request.request_metadata.caller)
      return DbRequest.objects.log_request(grpc_request = request)

    logged_request = self._handle_response(method = method)
    response = LogRequestResponse()
    response.request_id = logged_request.pk
    return response

  def LogResponse(self, request: ResponseRequest, _: grpc.ServicerContext) -> LogStandardResponse :
    """Log request responses."""
    self._handle_response(method = lambda: DbRequest.objects.log_response(grpc_response = request))
    return LogStandardResponse()


  def _handle_response(self, *, method: Callable[[], Metadata]) -> Metadata :
    """Wrap responses for logging."""
    try:
      metadata = method()
      if metadata.meta_logging_errors:
        # Caught by KhaleesiException and  re-raised
        raise InvalidArgumentException(private_details = metadata.meta_logging_errors)
      return metadata
    except KhaleesiException as exception:
      raise exception from None
    except Exception as exception:  # pylint: disable=broad-except
      raise InternalServerException(
        private_details = f'{type(exception).__name__}: {str(exception)}',
      ) from exception


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
