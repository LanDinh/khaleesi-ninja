"""Check job execution status for an app."""

# Python.
from typing import Dict, List, cast
from uuid import uuid4

# Django.
from django.core.paginator import Page
from django.db import models, transaction

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.batch.job import CleanupJob
from khaleesi.core.batch.jobExecutionMixin import IN_PROGRESS
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.core.grpc.requestMetadata import addSystemRequestMetadata
from khaleesi.core.singleton.structured_logger import SINGLETON
from khaleesi.proto.core_pb2 import (
  JobExecutionRequest,
  Action,
  JobExecutionList,
  ObjectMetadataListRequest,
  JobExecution as GrpcJobExecution,
)
from khaleesi.proto.core_pb2_grpc import MaidStub
from microservice.models.jobExecution import JobExecution


class UpdateExecutionStateJob(CleanupJob[JobExecution]):
  """Check job execution status for an app."""

  action       : Action
  httpRequestId: str
  grpcRequestId: str
  method = 'UPDATE_JOB_EXECUTION_STATE'

  def __init__(self, *, action: Action, request: JobExecutionRequest) -> None :
    """Initialize the job."""
    super().__init__(model = JobExecution, request = request)
    self.action        = action
    self.httpRequestId = str(uuid4())
    channel   = CHANNEL_MANAGER.getChannel(site = action.site, app = action.app)
    self.stub = MaidStub(channel)  # type: ignore[no-untyped-call]
    SINGLETON.structuredLogger.logHttpRequest(
      httpRequestId = self.httpRequestId,
      method        = self.method,
    )

  def executeBatch(self, *, page: Page[JobExecution]) -> int :
    """Execute a batch."""
    with transaction.atomic():
      # Send out the request to fetch the updated states.
      instances: Dict[str, JobExecution] = {}
      for instance in page.object_list:
        instances[instance.khaleesiId] = instance
      jobExecutions = self.getUpdatedJobExecutionState(instances = instances)
      # Handle the updated states.
      instancesForSaving: List[JobExecution] = []
      for grpc in jobExecutions.jobExecutions:
        instance = instances[grpc.executionMetadata.id]
        instance.khaleesiSave(grpc = grpc, metadata = instance.toObjectMetadata(), dbSave = False)
        instancesForSaving.append(instance)
      # noinspection PyProtectedMember
      fields = [field.name for field in JobExecution._meta.get_fields()]
      return JobExecution.objects.bulk_update(instancesForSaving, fields = fields)

  def getQueryset(self) -> models.QuerySet[JobExecution] :
    """Get the next page to be worked on."""
    return JobExecution.objects.getJobExecutionsInProgress(action = self.action)

  def finishJob(self) -> None :
    """Clean up requests."""
    if self.jobExecution.hasStatus(grpc = GrpcJobExecution.Status.UNKNOWN):
      status = StatusCode.UNKNOWN
    elif self.jobExecution.status in IN_PROGRESS:
      status = StatusCode.UNKNOWN
    elif self.jobExecution.hasStatus(grpc = GrpcJobExecution.Status.SUCCESS):
      status = StatusCode.OK
    elif self.jobExecution.hasStatus(grpc = GrpcJobExecution.Status.TIMEOUT):
      status = StatusCode.DEADLINE_EXCEEDED
    elif self.jobExecution.hasStatus(grpc = GrpcJobExecution.Status.ABORT):
      status = StatusCode.ABORTED
    elif self.jobExecution.hasStatus(grpc = GrpcJobExecution.Status.ERROR):
      status = StatusCode.INTERNAL
    elif self.jobExecution.hasStatus(grpc = GrpcJobExecution.Status.SKIPPED):
      status = StatusCode.ALREADY_EXISTS
    elif self.jobExecution.hasStatus(grpc = GrpcJobExecution.Status.FATAL):
      status = StatusCode.INTERNAL
    else:
      status = StatusCode.UNIMPLEMENTED
    SINGLETON.structuredLogger.logHttpResponse(
      httpRequestId = self.httpRequestId,
      method        = self.method,
      status        = status
    )

  def getUpdatedJobExecutionState(self, *, instances: Dict[str, JobExecution]) -> JobExecutionList :
    """Get the updated job execution states based on the list of job executions."""
    jobExecutionIds = ObjectMetadataListRequest()
    addSystemRequestMetadata(
      metadata      = jobExecutionIds.metadata,
      httpRequestId = self.httpRequestId,
      grpcRequestId = str(uuid4()),
      method        = self.method,
    )
    for instance in instances.values():
      jobExecutionIds.objects.objects.append(instance.toObjectMetadata())
    return cast(JobExecutionList, self.stub.FetchExecutionState(jobExecutionIds))
