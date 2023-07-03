"""Sawyer service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.batch.executor import jobExecutor
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.proto.core_pb2 import EmptyResponse, JobExecutionRequest
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
  add_SawyerServicer_to_server as addToServer
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

  def CleanupEvents(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up events older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbEvent, request = request))

  def CleanupGrpcRequests(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up requests older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbGrpcRequest, request = request))

  def CleanupErrors(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up errors older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbError, request = request))

  def CleanupHttpRequests(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up HTTP requests older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbHttpRequest, request = request))

  def CleanupQueries(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up queries older than '
      f'{request.cleanupConfiguration.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbQuery, request = request))

  def GetEvents(self, request: LogFilter, _: grpc.ServicerContext) -> EventsList :
    """Get logged events."""
    result = EventsList()
    LOGGER.info('Getting all events.')
    for event in DbEvent.objects.filter():
      result.events.append(event.toGrpc())
    return result

  def GetHttpRequests(self, request: LogFilter, _: grpc.ServicerContext) -> HttpRequestList:
    """Get logged requests."""
    result = HttpRequestList()
    LOGGER.info('Getting all HTTP requests.')
    for dbHttpRequest in DbHttpRequest.objects.filter():
      result.requests.append(dbHttpRequest.toGrpc())
    return result

  def GetGrpcRequests(self, request: LogFilter, _: grpc.ServicerContext) -> GrpcRequestList :
    """Get logged requests."""
    result = GrpcRequestList()
    LOGGER.info('Getting all requests.')
    for dbRequest in DbGrpcRequest.objects.filter():
      result.requests.append(dbRequest.toGrpc())
    return result

  def GetQueries(self, request: LogFilter, _: grpc.ServicerContext) -> QueryList :
    """Get logged queries."""
    result = QueryList()
    LOGGER.info('Getting all queries.')
    for dbQuery in DbQuery.objects.filter():
      result.queries.append(dbQuery.toGrpc())
    return result

  def GetErrors(self, request: LogFilter, _: grpc.ServicerContext) -> ErrorList :
    """Get logged errors."""
    result = ErrorList()
    LOGGER.info('Getting all errors.')
    for dbError in DbError.objects.filter():
      result.errors.append(dbError.toGrpc())
    return result


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Sawyer'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
