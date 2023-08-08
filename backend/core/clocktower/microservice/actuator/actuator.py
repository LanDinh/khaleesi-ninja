"""Actuate batch jobs."""

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.proto.core_pb2 import (
  ObjectMetadata,
  JobExecutionRequest,
  JobExecution as GrpcJobExecution,
)
from microservice.actuator.core import CORE
from microservice.models.jobExecution import JobExecution as DbJobExecution


class Actuator:
  """Actuate batch jobs for a specific app."""

  actions = {
      'core': CORE
  }

  def actuate(self, *, action: str, request: JobExecutionRequest) -> ObjectMetadata :
    """Actuate a batch job request."""
    parts = action.split('.')
    if len(parts) != 3:
      raise InvalidArgumentException(
        publicDetails  = f'actionName = ${action}',
        privateMessage = 'actionName has the wrong format.',
        privateDetails = f'actionName = ${action}',
      )
    site = parts[0]
    app  = parts[1]
    name = parts[2]
    # Register execution attempt.
    execution = DbJobExecution.objects.khaleesiCreate(grpc = request.jobExecution)
    try:
      # Execute actuator.
      method = self.actions[site][app][name]
      method(request)
      # Return execution metadata.
      return execution.toObjectMetadata()
    except KeyError as exception:
      request.jobExecution.status = GrpcJobExecution.Status.FATAL
      request.jobExecution.statusDetails = f'The action ${site}.${app}.${action} does not exist.'
      execution.khaleesiSave(grpc = request.jobExecution, metadata = execution.toObjectMetadata())
      raise InvalidArgumentException(
        publicDetails  = f'site = ${site}, app = ${app}, action = ${action}',
        privateMessage = 'No such action exists.',
        privateDetails = f'site = ${site}, app = ${app}, action = ${action}',
      ) from exception


ACTUATOR = Actuator()
