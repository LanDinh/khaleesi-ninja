"""Sawyer service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import (
  DESCRIPTOR,
  LogFilter,
  EventsList,
  RequestList,
  ErrorList,
  BackgateRequestList,
  QueryList,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
  SawyerServicer as Servicer,
  add_SawyerServicer_to_server as add_to_server
)
from microservice.models import (
  Event as DbEvent,
  Request as DbRequest,
  Error as DbError,
  BackgateRequest as DbBackgateRequest,
  Query as DbQuery,
)


class Service(Servicer):
  """Sawyer service."""

  def GetEvents(self, request: LogFilter, _: grpc.ServicerContext) -> EventsList :
    """Get logged events."""
    result = EventsList()
    LOGGER.info('Getting all events.')
    for event in DbEvent.objects.filter():
      result.events.append(event.to_grpc_event_response())
    return result

  def GetBackgateRequests(self, request: LogFilter, _: grpc.ServicerContext) -> BackgateRequestList:
    """Get logged requests."""
    result = BackgateRequestList()
    LOGGER.info('Getting all backgate requests.')
    for db_backgate_request in DbBackgateRequest.objects.filter():
      result.requests.append(db_backgate_request.to_grpc_backgate_request_response())
    return result

  def GetRequests(self, request: LogFilter, _: grpc.ServicerContext) -> RequestList :
    """Get logged requests."""
    result = RequestList()
    LOGGER.info('Getting all requests.')
    for db_request in DbRequest.objects.filter():
      result.requests.append(db_request.to_grpc_request_response())
    return result

  def GetQueries(self, request: LogFilter, _: grpc.ServicerContext) -> QueryList :
    """Get logged queries."""
    result = QueryList()
    LOGGER.info('Getting all queries.')
    for db_query in DbQuery.objects.filter():
      result.queries.append(db_query.to_grpc_query_response())
    return result

  def GetErrors(self, request: LogFilter, _: grpc.ServicerContext) -> ErrorList :
    """Get logged errors."""
    result = ErrorList()
    LOGGER.info('Getting all errors.')
    for db_error in DbError.objects.filter():
      result.errors.append(db_error.to_grpc_error_response())
    return result


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Sawyer'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
