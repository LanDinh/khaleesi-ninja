"""Thread utility."""

# Python.
from threading import Thread, Event
from typing import Generic

# khaleesi.ninja.
from khaleesi.core.batch.job import BaseJob, M
from khaleesi.proto.core_pb2 import JobExecutionMetadata


class BatchJobThread(Thread, Generic[M]):
  """Thread utility class."""

  stop_event         : Event
  job                : BaseJob[M]
  is_batch_job_thread: bool

  def __init__(self, *, job: BaseJob[M]) -> None :
    """Init the thread."""
    super().__init__()
    self.stop_event = Event()
    self.job = job
    self.is_batch_job_thread = True

  def run(self) -> None :
    """Run the job."""
    self.job.execute(stop_event = self.stop_event)

  def stop(self) -> None :
    """Stop the current thread object."""
    self.stop_event.set()

  def is_job(self, *, job: JobExecutionMetadata) -> bool :
    """Check if the job is the one asked for."""
    return self.job.job.jobId == job.jobId and self.job.job.executionId == job.executionId
