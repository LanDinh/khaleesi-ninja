"""Sawyer service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.batch.executor import job_executor
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_pb2 import EmptyResponse, JobRequest
from khaleesi.proto.core_sawmill_pb2 import (
  DESCRIPTOR,
  LogFilter,
  EventsList,
  GrpcRequestList,
  ErrorList,
  HttpRequestList,
  QueryList,
)
from khaleesi.proto.core_sawmill_pb2_grpc import (
  SawyerServicer as Servicer,
  add_SawyerServicer_to_server as add_to_server
)
from microservice.models import (
  Event as DbEvent,
  GrpcRequest as DbGrpcRequest,
  Error as DbError,
  HttpRequest as DbHttpRequest,
  Query as DbQuery,
)
from microservice.models.cleanup import CleanupJob


class Service(Servicer):
  """Sawyer service."""

  def CleanupEvents(self, request: JobRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up events older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return job_executor(job = CleanupJob(model = DbEvent, request = request))

  def CleanupGrpcRequests(self, request: JobRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up requests older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return job_executor(job = CleanupJob(model = DbGrpcRequest, request = request))

  def CleanupErrors(self, request: JobRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up errors older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return job_executor(job = CleanupJob(model = DbError, request = request))

  def CleanupHttpRequests(self, request: JobRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up HTTP requests older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return job_executor(job = CleanupJob(model = DbHttpRequest, request = request))

  def CleanupQueries(self, request: JobRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up queries older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return job_executor(job = CleanupJob(model = DbQuery, request = request))

  def GetEvents(self, request: LogFilter, _: grpc.ServicerContext) -> EventsList :
    """Get logged events."""
    result = EventsList()
    LOGGER.info('Getting all events.')
    for event in DbEvent.objects.filter():
      result.events.append(event.to_grpc_event_response())
    return result

  def GetHttpRequests(self, request: LogFilter, _: grpc.ServicerContext) -> HttpRequestList:
    """Get logged requests."""
    result = HttpRequestList()
    LOGGER.info('Getting all HTTP requests.')
    for db_http_request in DbHttpRequest.objects.filter():
      result.requests.append(db_http_request.to_grpc_backgate_request_response())
    return result

  def GetGrpcRequests(self, request: LogFilter, _: grpc.ServicerContext) -> GrpcRequestList :
    """Get logged requests."""
    result = GrpcRequestList()
    LOGGER.info('Getting all requests.')
    for db_request in DbGrpcRequest.objects.filter():
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
