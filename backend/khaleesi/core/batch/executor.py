"""Executor for jobs."""

# khaleesi.ninja.
from khaleesi.core.batch.job import BaseJob, M
from khaleesi.core.batch.thread import BatchJobThread
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import EmptyResponse

def jobExecutor(*, job: BaseJob[M]) -> EmptyResponse :
  """Execute a job."""
  thread = BatchJobThread(job = job, stateRequest = STATE.request, stateQueries = STATE.queries)
  thread.start()
  return EmptyResponse()
