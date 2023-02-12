"""Thread utility."""

# Python.
from threading import Thread, Event
from typing import Generic

# khaleesi.ninja.
from khaleesi.core.batch.job import BaseJob, M
from khaleesi.proto.core_pb2 import JobExecutionMetadata


class BatchJobThread(Thread, Generic[M]):
  """Thread utility class."""

  stop_event: Event
  job       : BaseJob[M]

  def __init__(self, *, job: BaseJob[M]) -> None :
    """Init the thread."""
    super().__init__()
    self.stop_event = Event()
    self.job = job

  def run(self) -> None :
    """Run the job."""
    self.job.execute()

  def stop(self) -> None :
    """Stop the current thread object."""
    self.stop_event.set()

  @property
  def is_stopped(self) -> bool :
    """Check if the thread has been stopped."""
    return self.stop_event.is_set()

  def is_job(self, *, job: JobExecutionMetadata) -> bool :
    """Check if the job is the one asked for."""
    return self.job.job.job_id == job.job_id and self.job.job.execution_id == job.execution_id
