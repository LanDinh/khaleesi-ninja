"""Actuate batch jobs."""

# khaleesi.ninja.
from khaleesi.core.grpc.requestMetadata import addRequestMetadata
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.proto.core_pb2 import (
  ObjectMetadata,
  JobExecutionRequest,
  JobExecution as GrpcJobExecution,
)
from microservice.actuator.core import CORE
from microservice.models.job import Job
from microservice.models.jobExecution import JobExecution as DbJobExecution


class Actuator:
  """Actuate batch jobs for a specific app."""

  actions = {
      'core': CORE
  }

  def actuate(self, *, jobId: str) -> ObjectMetadata :
    """Actuate a batch job request."""
    # Register execution attempt.
    job = Job.objects.get(khaleesiId = jobId)
    grpc = job.toGrpcJobExecutionRequest()
    action = grpc.action
    instance = DbJobExecution.objects.khaleesiCreate(grpc = grpc)
    try:
      # Execute actuator.
      request = JobExecutionRequest()
      addRequestMetadata(metadata = request.requestMetadata)
      request.jobExecution.CopyFrom(instance.toGrpc())
      method = self.actions[action.site][action.app][action.action]
      method(request)
      # Return execution metadata.
      return instance.toObjectMetadata()
    except KeyError as exception:
      grpc.status = GrpcJobExecution.Status.FATAL
      grpc.statusDetails = f'No action "{action.site}.{action.app}.{action.action}"'
      instance.khaleesiSave(grpc = grpc, metadata = instance.toObjectMetadata())
      raise InvalidArgumentException(
        publicDetails  = f'site = {action.site}, app = {action.app}, action = {action.action}',
        privateMessage = 'No such action exists.',
        privateDetails = f'site = {action.site}, app = {action.app}, action = {action.action}',
      ) from exception


ACTUATOR = Actuator()
