"""Actuate batch jobs."""

# khaleesi.ninja.
from khaleesi.core.grpc.requestMetadata import addRequestMetadata
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.proto.core_pb2 import (
  JobExecutionMetadata,
  JobActionConfiguration,
  JobCleanupActionConfiguration,
  JobRequest,
  EmptyResponse,
)
from microservice.actuator.core import CORE


class Actuator:
  """Actuate batch jobs for a specific service."""

  actions = {
      'core': CORE
  }

  def actuate(
      self, *,
      actionName: str,
      job       : JobExecutionMetadata,
      action    : JobActionConfiguration,
      cleanup   : JobCleanupActionConfiguration,
  ) -> EmptyResponse :
    """Actuate a batch job request."""
    parts        = actionName.split('.')
    if len(parts) != 3:
      raise InvalidArgumentException(
        publicDetails  = f'actionName = ${actionName}',
        privateMessage = 'actionName has the wrong format.',
        privateDetails = f'actionName = ${actionName}',
      )
    gate    = parts[0]
    service = parts[1]
    name    = parts[2]
    try:
      method = self.actions[gate][service][name]
      return method(self._request(job = job, action = action, cleanup = cleanup))
    except KeyError as exception:
      raise InvalidArgumentException(
        publicDetails  = f'gate = ${gate}, service = ${service}, action = ${action}',
        privateMessage = 'No such action exists.',
        privateDetails = f'gate = ${gate}, service = ${service}, action = ${action}',
      ) from exception

  def _request(
      self, *,
      job    : JobExecutionMetadata,
      action : JobActionConfiguration,
      cleanup: JobCleanupActionConfiguration,
  ) -> JobRequest :
    """Build a JobRequest."""
    request = JobRequest()
    addRequestMetadata(request = request)
    request.job.jobId       = job.jobId
    request.job.executionId = job.executionId
    request.actionConfiguration.timelimit.FromTimedelta(action.timelimit.ToTimedelta())
    request.actionConfiguration.batchSize = action.batchSize
    request.cleanupConfiguration.cleanupDelay.FromTimedelta(cleanup.cleanupDelay.ToTimedelta())
    return request


ACTUATOR = Actuator()
