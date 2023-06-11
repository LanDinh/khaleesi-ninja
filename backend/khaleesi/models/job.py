"""Basic job tracking."""

# Django.
from django.db import models, transaction

# khaleesi.ninja.
from khaleesi.core.grpc.request_metadata import add_request_metadata
from khaleesi.proto.core_pb2 import JobExecutionMetadata, JobExecutionResponse


IN_PROGRESS = JobExecutionResponse.Status.Name(JobExecutionResponse.Status.IN_PROGRESS)


class JobExecutionManager(models.Manager['JobExecution']):
  """Basic job manager."""

  def start_job_execution(self, *, job: JobExecutionMetadata) -> 'JobExecution' :
    """Register job start. Returns whether the job should start or not."""
    with transaction.atomic(using = 'write'):
      in_progress_count = self.filter(job_id = job.job_id, status = IN_PROGRESS).count()
      if in_progress_count > 0:
        return self.create(job_id = job.job_id, execution_id = job.execution_id, status = 'SKIPPED')
      return self.create(job_id = job.job_id, execution_id = job.execution_id, status = IN_PROGRESS)

class JobExecution(models.Model):
  """Basic job."""
  job_id          = models.TextField(default = 'UNKNOWN')
  execution_id    = models.BigIntegerField(default = -1)
  status          = models.TextField(default = 'UNKNOWN')
  end             = models.DateTimeField(auto_now = True)
  items_processed = models.IntegerField(default = 0)
  total_items     = models.IntegerField(default = 0)
  details         = models.TextField(default = '')

  objects = JobExecutionManager()

  @property
  def in_progress(self) -> bool :
    """Specify if the job is in progress."""
    return self.status == IN_PROGRESS

  def set_total(self, *, total: int) -> None :
    """Set the total amount of items for the job."""
    self.total_items = total
    self.save()

  def finish(
      self, *,
      status         : 'JobExecutionResponse.Status.V',
      items_processed: int,
      details        : str,
  ) -> None :
    """Register job finish."""
    self.status          = JobExecutionResponse.Status.Name(status)
    self.items_processed = items_processed
    self.details         = details
    self.save()

  def to_grpc_job_execution_response(self) -> JobExecutionResponse :
    """Transform into gRPC."""
    response = JobExecutionResponse()
    add_request_metadata(request = response)
    response.execution_metadata.job_id       = self.job_id
    response.execution_metadata.execution_id = self.execution_id
    response.status          = JobExecutionResponse.Status.Value(self.status)
    response.items_processed = self.items_processed
    response.total_items     = self.total_items
    response.details         = self.details
    response.end.FromDatetime(self.end)
    return response
