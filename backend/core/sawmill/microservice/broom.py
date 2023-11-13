"""Maid service."""

# khaleesi-ninja.
from khaleesi.core.batch.broom import BaseBroom
from khaleesi.core.batch.executor import jobExecutor
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.proto.core_pb2 import EmptyResponse, JobExecutionRequest
from microservice.models import (
  Event as DbEvent,
  GrpcRequest as DbGrpcRequest,
  Error as DbError,
  HttpRequest as DbHttpRequest,
  Query as DbQuery,
)
from microservice.models.cleanupJob import CleanupJob


class Broom(BaseBroom):
  """Maid service."""

  def cleanup(self, *, jobExecutionRequest: JobExecutionRequest) -> EmptyResponse :
    """Cleanup stuff."""
    if jobExecutionRequest.jobExecution.action.action == 'cleanup-events':
      return jobExecutor(job = CleanupJob(model = DbEvent, request = jobExecutionRequest))
    elif jobExecutionRequest.jobExecution.action.action == 'cleanup-grpc-requests':
      return jobExecutor(job = CleanupJob(model = DbGrpcRequest, request = jobExecutionRequest))
    elif jobExecutionRequest.jobExecution.action.action == 'cleanup-errors':
      return jobExecutor(job = CleanupJob(model = DbError, request = jobExecutionRequest))
    elif jobExecutionRequest.jobExecution.action.action == 'cleanup-http-requests':
      return jobExecutor(job = CleanupJob(model = DbHttpRequest, request = jobExecutionRequest))
    elif jobExecutionRequest.jobExecution.action.action == 'cleanup-queries':
      return jobExecutor(job = CleanupJob(model = DbQuery, request = jobExecutionRequest))
    else:
      raise ProgrammingException(
        privateMessage = 'Cleanup action isn\'t implemented!',
        privateDetails = jobExecutionRequest.jobExecution.action.action,
      )
