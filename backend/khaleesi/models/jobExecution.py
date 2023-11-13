"""Basic job tracking."""

from __future__ import annotations

# Python.
from datetime import datetime
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.batch.jobExecutionMixin import JobExecutionMixin, IN_PROGRESS
from khaleesi.core.models.baseModel import Model, Manager
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution, ObjectMetadata




class JobExecutionManager(Manager['JobExecution']):
  """Basic job execution manager."""

  def countJobExecutionsInProgress(self, *, job: ObjectMetadata) -> int :
    """Count how many jobs are in progress."""
    return self.filter(jobId = job.id, status__in = IN_PROGRESS).count()

  def getJobExecutionsInProgress(self, *, job: ObjectMetadata) -> List[GrpcJobExecution] :
    """Stop the job with the given job ID."""
    jobObjects = self.filter(jobId = job.id, status__in = IN_PROGRESS)
    jobs: List[GrpcJobExecution] = []
    for jobObject in jobObjects:
      grpc = GrpcJobExecution()
      grpc.jobMetadata.id       = jobObject.jobId
      grpc.executionMetadata.id = jobObject.executionId
      jobs.append(grpc)

    return jobs


class JobExecution(Model[GrpcJobExecution], JobExecutionMixin):
  """Basic job execution."""
  # Metadata.
  executionId = models.TextField(unique = True)

  objects: JobExecutionManager = JobExecutionManager()  # type: ignore[assignment]

  def setTotal(self, *, total: int) -> None :
    """Set the total amount of items for the job."""
    metadata = self.toObjectMetadata()
    grpc = self.toGrpc()
    grpc.totalItems = total
    self.khaleesiSave(metadata = metadata, grpc = grpc)

  def finish(
      self, *,
      status        : 'GrpcJobExecution.Status.V',
      itemsProcessed: int,
      statusDetails : str,
  ) -> None :
    """Register job finish."""
    metadata = self.toObjectMetadata()
    grpc = self.toGrpc()
    grpc.status         = status
    grpc.itemsProcessed = itemsProcessed
    grpc.statusDetails  = statusDetails
    grpc.end.FromDatetime(datetime.now())
    self.khaleesiSave(metadata = metadata, grpc = grpc)

  def khaleesiSave(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcJobExecution,
      dbSave  : bool = True,
  ) -> None :
    """Change own values according to the grpc object."""
    if self._state.adding:
      self.executionId = grpc.executionMetadata.id
    self.jobExecutionFromGrpc(grpc = grpc)
    super().khaleesiSave(metadata = metadata, grpc = grpc, dbSave = dbSave)

  def toGrpc(self) -> GrpcJobExecution :
    """Return a grpc object containing own values."""
    # Metadata.
    grpc = self.jobExecutionToGrpc()
    grpc.executionMetadata.id = self.executionId
    return grpc
