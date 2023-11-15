"""Actuate batch jobs."""

# khaleesi.ninja.
from khaleesi.core.grpc.requestMetadata import addRequestMetadata
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.proto.core_pb2 import (
  ObjectMetadata,
  JobExecutionRequest,
  JobExecution as GrpcJobExecution,
  Action,
)
from microservice.actuator.core import CORE
from microservice.actuator.core.clocktower import addAppForUpdateJobExecutionStateGenerator
from microservice.models.job import Job
from microservice.models.jobExecution import JobExecution as DbJobExecution


class Actuator:
  """Actuate batch jobs for a specific app."""

  actions = {
      'core': CORE
  }

  def __init__(self) -> None :
    """Initiate the actions that affect all apps."""
    LOGGER.debug('Adding actions that exist for all apps...')
    for siteName, siteObject in self.actions.items():
      for app in siteObject:
        action = Action()
        action.site = siteName
        action.app = app
        addAppForUpdateJobExecutionStateGenerator(action = action)


  def actuate(self, *, jobId: str) -> ObjectMetadata :
    """Actuate a batch job request."""
    # Register execution attempt.
    job = Job.objects.get(khaleesiId = jobId)
    grpc = job.toGrpcJobExecutionRequest()
    action = grpc.action
    instance = DbJobExecution.objects.khaleesiCreate(grpc = grpc)
    try:
      # Execute actuator.
      method = self.actions[action.site][action.app][action.action]
      request = JobExecutionRequest()
      addRequestMetadata(metadata = request.requestMetadata)
      request.jobExecution.CopyFrom(instance.toGrpc())
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
