"""Thread utility."""

# Python.
from threading import Thread, Event, enumerate as threadingEnumerate
from typing import Generic, List

# khaleesi.ninja.
from khaleesi.core.batch.job import BaseJob, M
from khaleesi.proto.core_pb2 import ObjectMetadata, JobExecution, RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import Query


class BatchJobThread(Thread, Generic[M]):
  """Thread utility class."""

  stopEvent       : Event
  job             : BaseJob[M]
  isBatchJobThread: bool
  stateRequest    : RequestMetadata
  stateQueries         : List[Query]

  def __init__(
      self, *,
      job         : BaseJob[M],
      stateRequest: RequestMetadata,
      stateQueries: List[Query],
  ) -> None :
    """Init the thread."""
    super().__init__()
    self.stopEvent        = Event()
    self.job              = job
    self.isBatchJobThread = True
    self.stateRequest     = RequestMetadata()
    self.stateQueries     = []
    self.stateRequest.CopyFrom(stateRequest)
    for sourceQuery in stateQueries:
      query = Query()
      query.CopyFrom(sourceQuery)
      self.stateQueries.append(query)

  def run(self) -> None :
    """Run the job."""
    from khaleesi.core.shared.state import STATE  # pylint: disable=import-outside-toplevel
    STATE.copyFrom(request = self.stateRequest, queries = self.stateQueries)
    self.job.execute(stopEvent = self.stopEvent)

  def stop(self) -> None :
    """Stop the current thread object."""
    self.stopEvent.set()

  def isJob(self, *, job: ObjectMetadata) -> bool :
    """Check if the job is the one asked for."""
    return self.job.request.jobMetadata.id == job.id

def stopAllJobs() -> List[Thread] :
  """Stop all jobs."""
  threads: List[Thread] = []
  for thread in threadingEnumerate():
    if hasattr(thread, 'isBatchJobThread'):
      thread.stop()  # type: ignore[attr-defined]
      threads.append(thread)
  return threads

def stopJob(jobs: List[JobExecution]) -> None :
  """Stop the given job."""
  for thread in threadingEnumerate():
    if hasattr(thread, 'isBatchJobThread'):
      # This is expected to have at most 1 element, but stop all executions just in case.
      for job in jobs:
        if thread.isJob(job = job):  # type: ignore[attr-defined]
          thread.stop()  # type: ignore[attr-defined]
