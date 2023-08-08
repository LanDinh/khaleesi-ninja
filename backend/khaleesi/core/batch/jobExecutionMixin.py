"""Utility for saving job configuration."""

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution


class JobExecutionMixin(models.Model):
  """Mixin for job configuration."""
  # Metadata.
  jobId = models.TextField()

  # Result.
  status        = models.TextField(default = 'UNKNOWN')
  end           = models.DateTimeField()
  statusDetails = models.TextField()

  # Statistics.
  itemsProcessed = models.IntegerField(default = 0)
  totalItems     = models.IntegerField(default = 0)

  class Meta:
    abstract = True

  @property
  def inProgress(self) -> bool :
    """Specify if the job is in progress."""
    return GrpcJobExecution.Status.Value(self.status) in [
        GrpcJobExecution.Status.IN_PROGRESS,
        GrpcJobExecution.Status.SCHEDULED,
    ]

  def jobExecutionFromGrpc(self, *, grpc: GrpcJobExecution) -> None :
    """Change own values according to the grpc object."""
    if self._state.adding:
      # Metadata.
      self.jobId = grpc.jobMetadata.id

      # Initial status may be SKIPPED, FATAL, ... - so we need to be flexible.
      self.status = GrpcJobExecution.Status.Name(grpc.status)

    # Setting the finishing information can only be done for in-progress job executions.
    elif self.inProgress:
      self.itemsProcessed = grpc.itemsProcessed
      self.statusDetails  = grpc.statusDetails
      self.status         = GrpcJobExecution.Status.Name(grpc.status)

    # This can be set only once.
    if not self.totalItems:
      self.totalItems = grpc.totalItems

  def jobExecutionToGrpc(self) -> GrpcJobExecution :
    """Return a grpc object containing own values."""
    # Metadata.
    grpc = GrpcJobExecution()
    grpc.jobMetadata.id = self.jobId

    # Result.
    if self.end:
      grpc.end.FromDatetime(self.end)
    grpc.status        = GrpcJobExecution.Status.Value(self.status)
    grpc.statusDetails = self.statusDetails

    # Statistics.
    grpc.itemsProcessed = self.itemsProcessed
    grpc.totalItems     = self.totalItems

    return grpc
