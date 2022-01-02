"""core-sawmill service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import DESCRIPTOR, Event, LogResponse
from khaleesi.proto.core_sawmill_pb2_grpc import SawmillServicer, add_SawmillServicer_to_server
from microservice.models import Event as DbEvent
from microservice.models.abstract import Metadata


class Service(SawmillServicer):
  """core-sawmill service."""

  def LogEvent(self, request: Event, _: grpc.ServicerContext) -> LogResponse :
    """Log events."""
    return self._handle_response(method = lambda: DbEvent.objects.log_event(grpc_event = request))

  @staticmethod
  def _handle_response(*, method: Callable[[], Metadata]) -> LogResponse :
    """Wrap responses for logging."""
    response = LogResponse()
    try:
      metadata = method()
      if metadata.meta_logging_errors:
        response.result = LogResponse.ResultType.PARSING_ERROR
        response.errors = metadata.meta_logging_errors
      else:
        response.result = LogResponse.ResultType.SUCCESS
    except Exception as exception:  # pylint: disable=broad-except
      response.result = LogResponse.ResultType.FATAL_ERROR
      response.errors = f'{type(exception).__name__}: {str(exception)}'
    return response


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Sawmill'].full_name,
  add_service_to_server = add_SawmillServicer_to_server,
  service = Service()
)
