"""Executor for jobs."""

# khaleesi.ninja.
from khaleesi.core.batch.job import BaseJob, M
from khaleesi.core.batch.thread import BatchJobThread
from khaleesi.proto.core_pb2 import EmptyResponse

def job_executor(*, job: BaseJob[M]) -> EmptyResponse :
  """Execute a job."""
  thread = BatchJobThread(job = job)
  thread.start()
  return EmptyResponse()