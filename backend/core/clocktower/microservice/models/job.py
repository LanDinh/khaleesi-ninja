"""Job definitions."""

from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Manager
from khaleesi.core.models.eventIdModelOwnedBySystem import Model
from khaleesi.proto.core_pb2 import JobExecution, ObjectMetadata
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob
from microservice.models.jobConfigurationMixin import JobConfigurationMixin


class Job(Model[GrpcJob], JobConfigurationMixin):
  """Job definition"""
  name           = models.TextField(unique = True)
  description    = models.TextField()
  cronExpression = models.TextField()

  objects: Manager[Job]  # type: ignore[assignment]


  def toGrpcJobExecutionRequest(self) -> JobExecution :
    """Build a job start request based on the data of this job."""
    result = JobExecution()
    result.jobMetadata.id = self.khaleesiId
    self.jobConfigurationToGrpc(action = result.action, configuration = result.configuration)
    return result

  def khaleesiSave(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcJob,
      dbSave  : bool = True,
  ) -> None :
    """Change own values according to the grpc object."""
    self.name           = grpc.name
    self.description    = grpc.description
    self.cronExpression = grpc.cronExpression
    self.action         = grpc.action

    self.jobConfigurationFromGrpc(action = grpc.action, configuration = grpc.configuration)

    super().khaleesiSave(metadata = metadata, grpc = grpc, dbSave = dbSave)

  def toGrpc(self) -> GrpcJob :
    """Return a grpc object containing own values."""
    grpc = GrpcJob()

    grpc.name           = self.name
    grpc.description    = self.description
    grpc.cronExpression = self.cronExpression

    self.jobConfigurationToGrpc(action = grpc.action, configuration = grpc.configuration)

    return grpc
