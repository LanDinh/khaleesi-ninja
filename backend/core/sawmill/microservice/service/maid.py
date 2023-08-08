"""Maid service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.batch.executor import jobExecutor
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.proto.core_pb2 import EmptyResponse, JobExecutionRequest
from khaleesi.proto.core_sawmill_pb2 import DESCRIPTOR
from khaleesi.proto.core_sawmill_pb2_grpc import (
  MaidServicer as Servicer,
  add_MaidServicer_to_server as addToServer
)
from microservice.models import (
  Event as DbEvent,
  GrpcRequest as DbGrpcRequest,
  Error as DbError,
  HttpRequest as DbHttpRequest,
  Query as DbQuery,
)
from microservice.models.cleanupJob import CleanupJob


class Service(Servicer):
  """Maid service."""

  def CleanupHttpRequests(
      self,
      request: JobExecutionRequest,
      _      : grpc.ServicerContext,
  ) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up HTTP requests older than '
      f'{request.jobExecution.configuration.cleanup.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbHttpRequest, request = request))

  def CleanupGrpcRequests(
      self,
      request: JobExecutionRequest,
      _      : grpc.ServicerContext,
  ) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up requests older than '
      f'{request.jobExecution.configuration.cleanup.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbGrpcRequest, request = request))

  def CleanupEvents(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up events older than '
      f'{request.jobExecution.configuration.cleanup.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbEvent, request = request))

  def CleanupErrors(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up errors older than '
      f'{request.jobExecution.configuration.cleanup.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbError, request = request))

  def CleanupQueries(self, request: JobExecutionRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Clean up old data."""
    LOGGER.info(
      'Cleaning up queries older than '
      f'{request.jobExecution.configuration.cleanup.cleanupDelay.ToTimedelta()}.',
    )
    return jobExecutor(job = CleanupJob(model = DbQuery, request = request))


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Maid'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
