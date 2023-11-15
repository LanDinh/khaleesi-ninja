"""Basic job tracking."""

from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.batch.jobExecutionMixin import JobExecutionMixin, IN_PROGRESS
from khaleesi.core.models.baseModel import Manager
from khaleesi.core.models.idModel import Model
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution, ObjectMetadata, Action
from microservice.models.jobConfigurationMixin import JobConfigurationMixin


class JobExecutionManager(Manager['JobExecution']):
  """Basic job execution manager."""

  def getJobExecutionsInProgress(self, *, action: Action) -> models.QuerySet[JobExecution] :
    """Stop the job with the given job ID."""
    return self.filter(site = action.site, app = action.app, status__in = IN_PROGRESS)


class JobExecution(Model[GrpcJobExecution], JobConfigurationMixin, JobExecutionMixin):
  """Basic job execution."""

  start = models.DateTimeField(auto_now_add = True)

  objects = JobExecutionManager()  # type: ignore[assignment]

  def khaleesiSave(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcJobExecution,
      dbSave  : bool = True,
  ) -> None :
    """Change own values according to the grpc object."""
    self.jobExecutionFromGrpc(grpc = grpc)
    if self._state.adding:
      # Only update the configuration at creation.
      self.jobConfigurationFromGrpc(action = grpc.action, configuration = grpc.configuration)
      # Override any other state that might have been read from the request - for creation only.
      self.status = GrpcJobExecution.Status.Name(GrpcJobExecution.Status.SCHEDULED)
    super().khaleesiSave(metadata = metadata, grpc = grpc, dbSave = dbSave)

  def toGrpc(self) -> GrpcJobExecution :
    """Return a grpc object containing own values."""
    # Metadata.
    grpc = self.jobExecutionToGrpc()
    self.jobConfigurationToGrpc(action = grpc.action, configuration = grpc.configuration)
    grpc.executionMetadata.CopyFrom(self.toObjectMetadata())
    if self.start:
      grpc.start.FromDatetime(self.start)
    return grpc
