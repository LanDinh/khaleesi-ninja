"""Utility for saving job configuration."""

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution


IN_PROGRESS = [
    GrpcJobExecution.Status.Name(GrpcJobExecution.Status.IN_PROGRESS),
    GrpcJobExecution.Status.Name(GrpcJobExecution.Status.SCHEDULED),
]


class JobExecutionMixin(models.Model):
  """Mixin for job configuration."""
  # Metadata.
  jobId = models.TextField()

  # Result.
  status        = models.TextField(default = 'UNKNOWN')
  end           = models.DateTimeField(blank = True, null = True)
  statusDetails = models.TextField()

  # Statistics.
  itemsProcessed = models.IntegerField(default = 0)
  totalItems     = models.IntegerField(default = 0)

  class Meta:
    abstract = True

  @property
  def inProgress(self) -> bool :
    """Specify if the job is in progress."""
    return self.status in IN_PROGRESS

  def hasStatus(self, *, grpc: 'GrpcJobExecution.Status.V') -> bool :
    """Check if the job execution status matches the given gRPC status."""
    return self.status == GrpcJobExecution.Status.Name(grpc)

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

    if not self.inProgress:
      if grpc.end.ToDatetime():
        self.end = grpc.end.ToDatetime()

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
