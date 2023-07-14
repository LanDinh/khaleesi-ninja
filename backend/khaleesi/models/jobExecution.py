"""Basic job tracking."""

from __future__ import annotations

# Python.
from typing import List, Any

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.batch.jobConfigurationMixin import JobConfigurationMixin
from khaleesi.core.models.baseModel import Model
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution, ObjectMetadata


IN_PROGRESS = GrpcJobExecution.Status.Name(GrpcJobExecution.Status.IN_PROGRESS)


class JobExecutionManager(models.Manager['JobExecution']):
  """Basic job manager."""

  def countJobExecutionsInProgress(self, *, job: ObjectMetadata) -> int :
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


class JobExecution(Model[GrpcJobExecution], JobConfigurationMixin):
  """Basic job."""
  # Metadata.
  jobId       = models.TextField()
  executionId = models.TextField()

  # Result.
  status        = models.TextField(default = 'UNKNOWN')
  end           = models.DateTimeField()
  statusDetails = models.TextField()

  # Statistics.
  itemsProcessed = models.IntegerField(default = 0)
  totalItems     = models.IntegerField(default = 0)

  objects: JobExecutionManager = JobExecutionManager()

  @property
  def inProgress(self) -> bool :
    """Specify if the job is in progress."""
    return self.status == IN_PROGRESS

  def setTotal(self, *, total: int) -> None :
    """Set the total amount of items for the job."""
    metadata = ObjectMetadata()
    grpc = self.toGrpc(metadata = metadata)
    grpc.totalItems = total
    self.khaleesiSave(metadata = metadata, grpc = grpc)

  def finish(
      self, *,
      status        : 'GrpcJobExecution.Status.V',
      itemsProcessed: int,
      statusDetails : str,
  ) -> None :
    """Register job finish."""
    metadata = ObjectMetadata()
    grpc = self.toGrpc(metadata = metadata)
    grpc.status         = status
    grpc.itemsProcessed = itemsProcessed
    grpc.statusDetails  = statusDetails
    self.khaleesiSave(metadata = metadata, grpc = grpc)

  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcJobExecution,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    if self._state.adding:
      # Metadata.
      self.jobId       = grpc.jobMetadata.id
      self.executionId = grpc.executionMetadata.id

      # Job configuration.
      self.jobConfigurationFromGrpc(
        action  = grpc.actionConfiguration,
        cleanup = grpc.cleanupConfiguration,
      )

      # Necessary because IN_PROGRESS and SKIPPED are also a status.
      self.status = GrpcJobExecution.Status.Name(grpc.status)

    # Setting the finishing information can only be done for in-progress job executions.
    elif self.inProgress:
      self.itemsProcessed = grpc.itemsProcessed
      self.statusDetails  = grpc.statusDetails
      self.status         = GrpcJobExecution.Status.Name(grpc.status)

    # This can be set only once.
    if not self.totalItems:
      self.totalItems = grpc.totalItems

    super().khaleesiSave(metadata = metadata, grpc = grpc)

  def toGrpc(
      self, *,
      metadata: ObjectMetadata   = ObjectMetadata(),
      grpc    : GrpcJobExecution = GrpcJobExecution(),
  ) -> GrpcJobExecution :
    """Return a grpc object containing own values."""
    # Metadata.
    super().toGrpc(metadata = metadata, grpc = grpc)
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
