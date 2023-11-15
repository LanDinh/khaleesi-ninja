"""Test job utility."""

from khaleesi.proto.core_pb2 import JobExecutionRequest


class JobTestMixin:
  """Common methods for all job tests."""

  def buildRequest(self) -> JobExecutionRequest :
    """Prepare successful job start."""
    request = JobExecutionRequest()
    request.jobExecution.configuration.action.batchSize = 2
    request.jobExecution.configuration.action.timelimit.FromSeconds(60)
    return request

  def buildCleanupRequest(self) -> JobExecutionRequest :
    """Prepare successful cleanup job start."""
    request = self.buildRequest()
    request.jobExecution.configuration.cleanup.isCleanupJob = True
    return request
