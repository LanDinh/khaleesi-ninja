"""Basic job tracking."""

# Python.
from threading import Thread, enumerate as threading_enumerate
from typing import List

# Django.
from django.db import models, transaction

# khaleesi.ninja.
from khaleesi.core.grpc.requestMetadata import addRequestMetadata
from khaleesi.proto.core_pb2 import JobExecutionMetadata, JobExecutionResponse, IdMessage


IN_PROGRESS = JobExecutionResponse.Status.Name(JobExecutionResponse.Status.IN_PROGRESS)


class JobExecutionManager(models.Manager['JobExecution']):
  """Basic job manager."""

  def startJobExecution(self, *, job: JobExecutionMetadata) -> 'JobExecution' :
    """Register job start. Returns whether the job should start or not."""
    with transaction.atomic(using = 'write'):
      inProgressCount = self.filter(jobId = job.jobId, status = IN_PROGRESS).count()
      if inProgressCount > 0:
        return self.create(jobId = job.jobId, executionId = job.executionId, status = 'SKIPPED')
      return self.create(jobId = job.jobId, executionId = job.executionId, status = IN_PROGRESS)

  def stopJob(self, *, idMessage: IdMessage) -> None :
    """Stop the job with the given job ID."""
    jobObjects = self.filter(jobId = idMessage.id, status = IN_PROGRESS)
    jobs: List[JobExecutionMetadata] = []
    for jobObject in jobObjects:
      job             = JobExecutionMetadata()
      job.jobId       = jobObject.jobId
      job.executionId = jobObject.executionId
      jobs.append(job)
    for thread in threading_enumerate():
      if hasattr(thread, 'isBatchJobThread'):
        # This is expected to have at most 1 element, but stop all executions just in case.
        for job in jobs:
          temp = thread.isJob(job = job)  # type: ignore[attr-defined]
          if temp:
            thread.stop()  # type: ignore[attr-defined]

  def stopAllJobs(self) -> List[ Thread ] :
    """Stop all jobs."""
    threads: List[Thread] = []
    for thread in threading_enumerate():
      if hasattr(thread, 'isBatchJobThread'):
        thread.stop()  # type: ignore[attr-defined]
        threads.append(thread)
    return threads


class JobExecution(models.Model):
  """Basic job."""
  jobId          = models.TextField(default = 'UNKNOWN')
  executionId    = models.BigIntegerField(default = -1)
  status         = models.TextField(default = 'UNKNOWN')
  end            = models.DateTimeField(auto_now = True)
  itemsProcessed = models.IntegerField(default = 0)
  totalItems     = models.IntegerField(default = 0)
  details        = models.TextField(default = '')

  objects = JobExecutionManager()

  @property
  def inProgress(self) -> bool :
    """Specify if the job is in progress."""
    return self.status == IN_PROGRESS

  def setTotal(self, *, total: int) -> None :
    """Set the total amount of items for the job."""
    self.totalItems = total
    self.save()

  def finish(self, *,
      status        : 'JobExecutionResponse.Status.V',
      itemsProcessed: int,
      details       : str,
  ) -> None :
    """Register job finish."""
    self.status         = JobExecutionResponse.Status.Name(status)
    self.itemsProcessed = itemsProcessed
    self.details        = details
    self.save()

  def toGrpc(self) -> JobExecutionResponse :
    """Transform into gRPC."""
    response = JobExecutionResponse()
    addRequestMetadata(metadata = response.requestMetadata)
    response.executionMetadata.jobId       = self.jobId
    response.executionMetadata.executionId = self.executionId
    response.status         = JobExecutionResponse.Status.Value(self.status)
    response.itemsProcessed = self.itemsProcessed
    response.totalItems     = self.totalItems
    response.details        = self.details
    response.end.FromDatetime(self.end)
    return response
