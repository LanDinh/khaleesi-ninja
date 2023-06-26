"""Job definitions."""

# Python.
from __future__ import annotations
from datetime import timedelta
from typing import List, Tuple
from uuid import uuid4

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import DbObjectNotFoundException, DbObjectTwinException
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_pb2 import IdMessage, JobRequest
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob


class JobManager(models.Manager['Job']):
  """Custom model manager."""

  def createJob(self, *, grpcJob: GrpcJob) -> Job :
    """Create a new job."""
    errors: List[str] = []

    batchSize = grpcJob.actionConfiguration.batchSize \
      if grpcJob.actionConfiguration.batchSize else 1000
    timelimit = grpcJob.actionConfiguration.timelimit.ToTimedelta() \
      if grpcJob.actionConfiguration.timelimit.ToNanoseconds() > 0 else timedelta(hours = 1)

    return self.create(
      jobId          = str(uuid4()),
      name           = parseString(raw = grpcJob.name, name = 'name', errors = errors),
      description    = grpcJob.description,
      cronExpression = grpcJob.cronExpression,
      action         = parseString(raw = grpcJob.action, name = 'action', errors = errors),
      timelimit      = timelimit,
      batchSize      = batchSize,
      isCleanupJob   = grpcJob.cleanupConfiguration.isCleanupJob,
      cleanupDelay   = grpcJob.cleanupConfiguration.cleanupDelay.ToTimedelta(),
    )

  def getJobRequest(self, *, idMessage: IdMessage) -> Tuple[str, JobRequest] :
    """Build a job request based on DB data."""
    try:
      dbObject = self.get(jobId = idMessage.id)
      result = JobRequest()
      result.job.jobId = dbObject.jobId
      result.actionConfiguration.timelimit.FromTimedelta(dbObject.timelimit)
      result.actionConfiguration.batchSize = dbObject.batchSize
      result.cleanupConfiguration.cleanupDelay.FromTimedelta(dbObject.cleanupDelay)
      return dbObject.action, result
    except self.model.DoesNotExist as exception:
      raise DbObjectNotFoundException(objectType = 'Job') from exception
    except self.model.MultipleObjectsReturned as exception:
      raise DbObjectTwinException(objectType = 'Job', objectId = idMessage.id) from exception


class Job(models.Model):
  """Job definition"""
  jobId       = models.TextField(default = 'UNKNOWN', unique = True)
  name        = models.TextField(default = 'UNKNOWN', unique = True)
  description = models.TextField()

  # Common configuration.
  cronExpression = models.TextField()
  action         = models.TextField(default = 'UNKNOWN')
  timelimit      = models.DurationField(default = timedelta(hours = 1))
  batchSize      = models.IntegerField(default = 1000)

  # Cleanup.
  isCleanupJob = models.BooleanField(default = False)
  cleanupDelay = models.DurationField(default = timedelta())

  objects = JobManager()
