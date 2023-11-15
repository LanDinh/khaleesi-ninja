"""core-sawmill batch jobs."""

# khaleesi.ninja.
from khaleesi.core.batch.executor import jobExecutor
from khaleesi.proto.core_pb2 import JobExecutionRequest, EmptyResponse, Action
from microservice.batch.updateJobExecutionState import UpdateExecutionStateJob


CLOCKTOWER = {}


def addAppForUpdateJobExecutionStateGenerator(*, action: Action) -> None :
  """Add the UpdateJobExecutionState for the specified app."""
  def updateJobExecutionState(request: JobExecutionRequest) -> EmptyResponse :
    """Update the state of in-progress job executions."""
    return jobExecutor(job = UpdateExecutionStateJob(action = action, request = request))
  CLOCKTOWER[f'update-job-execution-state-{action.site}-{action.app}'] = updateJobExecutionState
