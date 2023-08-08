"""Job definitions."""

from __future__ import annotations

# Python.
from typing import Tuple, Any
from uuid import uuid4

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.batch.jobConfigurationMixin import JobConfigurationMixin
from khaleesi.core.grpc.requestMetadata import addRequestMetadata
from khaleesi.core.models.baseModel import Manager
from khaleesi.core.models.eventIdModelOwnedBySystem import Model
from khaleesi.proto.core_pb2 import JobExecutionRequest, ObjectMetadata
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob


class Job(Model[GrpcJob], JobConfigurationMixin):
  """Job definition"""
  name           = models.TextField(unique = True)
  description    = models.TextField()
  cronExpression = models.TextField()
  action         = models.TextField(default = 'UNKNOWN')

  objects: Manager[Job]  # type: ignore[assignment]


  def toGrpcJobExecutionRequest(self) -> Tuple[str, JobExecutionRequest] :
    """Build a job start request based on the data of this job."""
    result = JobExecutionRequest()
    addRequestMetadata(metadata = result.requestMetadata)
    result.jobExecution.jobMetadata.id = self.khaleesiId
    result.jobExecution.executionMetadata.id = str(uuid4())
    self.jobConfigurationToGrpc(
      action  = result.jobExecution.actionConfiguration,
      cleanup = result.jobExecution.cleanupConfiguration,
    )
    return self.action, result

  def khaleesiSave(
      self,
      *args   : Any,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcJob,
      **kwargs: Any,
  ) -> None :
    """Change own values according to the grpc object."""
    self.name           = grpc.name
    self.description    = grpc.description
    self.cronExpression = grpc.cronExpression
    self.action         = grpc.action

    self.jobConfigurationFromGrpc(
      action  = grpc.actionConfiguration,
      cleanup = grpc.cleanupConfiguration,
    )

    super().khaleesiSave(*args, metadata = metadata, grpc = grpc, **kwargs)

  def toGrpc(self) -> GrpcJob :
    """Return a grpc object containing own values."""
    grpc = GrpcJob()

    grpc.name           = self.name
    grpc.description    = self.description
    grpc.cronExpression = self.cronExpression
    grpc.action         = self.action

    self.jobConfigurationToGrpc(
      action  = grpc.actionConfiguration,
      cleanup = grpc.cleanupConfiguration,
    )

    return grpc
