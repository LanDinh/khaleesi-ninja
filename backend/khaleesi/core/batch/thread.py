"""Thread utility."""

# Python.
from threading import Thread, Event
from typing import Generic

# khaleesi.ninja.
from khaleesi.core.batch.job import BaseJob, M
from khaleesi.proto.core_pb2 import JobExecutionMetadata


class BatchJobThread(Thread, Generic[M]):
  """Thread utility class."""

  stopEvent       : Event
  job             : BaseJob[M]
  isBatchJobThread: bool

  def __init__(self, *, job: BaseJob[M]) -> None :
    """Init the thread."""
    super().__init__()
    self.stopEvent        = Event()
    self.job              = job
    self.isBatchJobThread = True

  def run(self) -> None :
    """Run the job."""
    self.job.execute(stopEvent = self.stopEvent)

  def stop(self) -> None :
    """Stop the current thread object."""
    self.stopEvent.set()

  def isJob(self, *, job: JobExecutionMetadata) -> bool :
    """Check if the job is the one asked for."""
    return self.job.job.jobId == job.jobId and self.job.job.executionId == job.executionId
