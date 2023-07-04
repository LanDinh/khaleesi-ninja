"""Basic job tracking."""

from __future__ import annotations

# Python.
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.batch.jobConfigurationMixin import JobConfigurationMixin
from khaleesi.core.models.baseModel import Model, ModelManager
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution, ObjectMetadata


IN_PROGRESS = GrpcJobExecution.Status.Name(GrpcJobExecution.Status.IN_PROGRESS)


class JobExecutionManager(ModelManager['JobExecution']):
  """Basic job manager."""

  def countJobsInProgress(self, *, job: ObjectMetadata) -> int :
    """Count how many jobs are in progress."""
    return self.filter(jobId = job.id, status = IN_PROGRESS).count()

  def getJobExecutionsInProgress(self, *, job: ObjectMetadata) -> List[GrpcJobExecution] :
    """Stop the job with the given job ID."""
    jobObjects = self.filter(jobId = job.id, status = IN_PROGRESS)
    jobs: List[GrpcJobExecution] = []
    for jobObject in jobObjects:
      grpc = GrpcJobExecution()
      grpc.jobMetadata.id       = jobObject.jobId
      grpc.executionMetadata.id = jobObject.executionId
      jobs.append(grpc)

    return jobs

  def baseKhaleesiGet(self, *, metadata: ObjectMetadata) -> JobExecution :
    """Get a job execution by ID."""
    return self.get(executionId = metadata.id)


class JobExecution(Model[GrpcJobExecution], JobConfigurationMixin):
  """Basic job."""
  # Metadata.
  jobId       = models.TextField()
  executionId = models.TextField()

  # Result.
  status         = models.TextField(default = 'UNKNOWN')
  end            = models.DateTimeField()
  statusDetails = models.TextField()

  # Statistics.
  itemsProcessed = models.IntegerField()
  totalItems     = models.IntegerField()

  objects: JobExecutionManager = JobExecutionManager()  # type: ignore[assignment]

  @property
  def inProgress(self) -> bool :
    """Specify if the job is in progress."""
    return self.status == IN_PROGRESS

  def setTotal(self, *, total: int) -> None :
    """Set the total amount of items for the job."""
    self.totalItems = total
    self.save()

  def finish(self, *,
      status        : 'GrpcJobExecution.Status.V',
      itemsProcessed: int,
      statusDetails : str,
  ) -> None :
    """Register job finish."""
    self.status         = GrpcJobExecution.Status.Name(status)
    self.itemsProcessed = itemsProcessed
    self.statusDetails  = statusDetails
    self.save()

  def fromGrpc(self, *, grpc: GrpcJobExecution) -> None :
    """Change own values according to the grpc object."""
    if not self.pk:
      # Metadata.
      self.jobId       = grpc.jobMetadata.id
      self.executionId = grpc.executionMetadata.id

      # Job configuration.
      self.jobConfigurationFromGrpc(
        action  = grpc.actionConfiguration,
        cleanup = grpc.cleanupConfiguration,
      )

      # Misc. Necessary because IN_PROGRESS and SKIPPED are also a status.
      self.status = GrpcJobExecution.Status.Name(grpc.status)

  def toGrpc(
      self, *,
      metadata: ObjectMetadata   = ObjectMetadata(),
      grpc    : GrpcJobExecution = GrpcJobExecution(),
  ) -> GrpcJobExecution :
    """Return a grpc object containing own values."""
    # Metadata.
    grpc = super().toGrpc(metadata = metadata, grpc = grpc)
    grpc.jobMetadata.id       = self.jobId
    grpc.executionMetadata.id = self.executionId

    # Job configuration.
    self.jobConfigurationToGrpc(
      action  = grpc.actionConfiguration,
      cleanup = grpc.cleanupConfiguration,
    )

    # Result.
    if self.end:
      grpc.end.FromDatetime(self.end)
    grpc.status        = GrpcJobExecution.Status.Value(self.status)
    grpc.statusDetails = self.statusDetails

    # Statistics.
    grpc.itemsProcessed = self.itemsProcessed
    grpc.totalItems     = self.totalItems

    return grpc
