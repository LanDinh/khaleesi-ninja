"""Actuate batch jobs."""

# khaleesi.ninja.
from khaleesi.core.grpc.request_metadata import add_request_metadata
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
      action_name: str,
      job        : JobExecutionMetadata,
      action     : JobActionConfiguration,
      cleanup    : JobCleanupActionConfiguration,
  ) -> EmptyResponse :
    """Actuate a batch job request."""
    parts        = action_name.split('.')
    if len(parts) != 3:
      raise InvalidArgumentException(
        public_details  = f'action_name = ${action_name}',
        private_message = 'action_name has the wrong format.',
        private_details = f'action_name = ${action_name}',
      )
    gate    = parts[0]
    service = parts[1]
    name    = parts[2]
    try:
      method = self.actions[gate][service][name]
      return method(self._request(job = job, action = action, cleanup = cleanup))
    except KeyError as exception:
      raise InvalidArgumentException(
        public_details  = f'gate = ${gate}, service = ${service}, action = ${action}',
        private_message = 'No such action exists.',
        private_details = f'gate = ${gate}, service = ${service}, action = ${action}',
      ) from exception

  def _request(
      self, *,
      job    : JobExecutionMetadata,
      action : JobActionConfiguration,
      cleanup: JobCleanupActionConfiguration,
  ) -> JobRequest :
    """Build a JobRequest."""
    request = JobRequest()
    add_request_metadata(request = request)
    request.job.job_id       = job.job_id
    request.job.execution_id = job.execution_id
    request.action_configuration.timelimit.FromTimedelta(action.timelimit.ToTimedelta())
    request.action_configuration.batch_size = action.batch_size
    request.cleanup_configuration.cleanup_delay.FromTimedelta(cleanup.cleanup_delay.ToTimedelta())
    return request


ACTUATOR = Actuator()
