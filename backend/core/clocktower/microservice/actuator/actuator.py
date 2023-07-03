"""Actuate batch jobs."""

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.proto.core_pb2 import (
  ObjectMetadata,
  JobExecutionRequest,
)
from microservice.actuator.core import CORE


class Actuator:
  """Actuate batch jobs for a specific service."""

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
    gate    = parts[0]
    service = parts[1]
    name    = parts[2]
    try:
      method = self.actions[gate][service][name]
      method(request)
      return request.jobExecution.executionMetadata
    except KeyError as exception:
      raise InvalidArgumentException(
        publicDetails  = f'gate = ${gate}, service = ${service}, action = ${action}',
        privateMessage = 'No such action exists.',
        privateDetails = f'gate = ${gate}, service = ${service}, action = ${action}',
      ) from exception


ACTUATOR = Actuator()
