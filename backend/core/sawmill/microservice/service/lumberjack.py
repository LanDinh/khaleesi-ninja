"""core-sawmill service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.exceptions import (
    KhaleesiException,
    InvalidArgumentException,
    InternalServerException,
)
from khaleesi.core.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import (
    DESCRIPTOR,
    Event,
    Request, LogRequestResponse,
    LogResponse,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
    LumberjackServicer as Servicer,
    add_LumberjackServicer_to_server as add_to_server
)
from microservice.models import Event as DbEvent, Request as DbRequest
from microservice.models.abstract import Metadata


class Service(Servicer):
  """core-sawmill service."""

  def LogEvent(self, request: Event, _: grpc.ServicerContext) -> LogResponse :
    """Log events."""
    self._handle_response(method = lambda: DbEvent.objects.log_event(grpc_event = request))
    return LogResponse()

  def LogRequest(self, request: Request, _: grpc.ServicerContext) -> LogRequestResponse :
    """Log requests."""
    logged_request = self._handle_response(
      method = lambda: DbRequest.objects.log_request(grpc_request = request),
    )
    response = LogRequestResponse()
    response.request_id = logged_request.pk
    return response


  @staticmethod
  def _handle_response(*, method: Callable[[], Metadata]) -> Metadata :
    """Wrap responses for logging."""
    try:
      metadata = method()
      if metadata.meta_logging_errors:
        raise InvalidArgumentException(
          public_details = '',
          private_details = metadata.meta_logging_errors,
        )
      return metadata
    except KhaleesiException as exception:
      raise exception from None
    except Exception as exception:  # pylint: disable=broad-except
      raise InternalServerException(
        public_details = '',
        private_details = f'{type(exception).__name__}: {str(exception)}',
      ) from exception


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
