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
from khaleesi.core.shared.parse_util import parse_string
from khaleesi.proto.core_pb2 import IdMessage, JobRequest
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob


class JobManager(models.Manager['Job']):
  """Custom model manager."""

  def create_job(self, *, grpc_job: GrpcJob) -> Job :
    """Create a new job."""
    errors: List[str] = []

    batch_size = grpc_job.action_configuration.batch_size \
      if grpc_job.action_configuration.batch_size else 1000
    timelimit = grpc_job.action_configuration.timelimit.ToTimedelta() \
      if grpc_job.action_configuration.timelimit.ToNanoseconds() > 0 else timedelta(hours = 1)

    return self.create(
      job_id          = str(uuid4()),
      name            = parse_string(raw = grpc_job.name, name = 'name', errors = errors),
      description     = grpc_job.description,
      cron_expression = grpc_job.cron_expression,
      action          = parse_string(raw = grpc_job.action, name = 'action', errors = errors),
      timelimit       = timelimit,
      batch_size      = batch_size,
      is_cleanup_job  = grpc_job.cleanup_configuration.is_cleanup_job,
      cleanup_delay   = grpc_job.cleanup_configuration.cleanup_delay.ToTimedelta(),
    )

  def get_job_request(self, *, id_message: IdMessage) -> Tuple[str, JobRequest] :
    """Build a job request based on DB data."""
    try:
      db_object = self.get(job_id = id_message.id)
      result = JobRequest()
      result.job.job_id = db_object.job_id
      result.action_configuration.timelimit.FromTimedelta(db_object.timelimit)
      result.action_configuration.batch_size = db_object.batch_size
      result.cleanup_configuration.cleanup_delay.FromTimedelta(db_object.cleanup_delay)
      return db_object.action, result
    except self.model.DoesNotExist as exception:
      raise DbObjectNotFoundException(object_type = 'Job') from exception
    except self.model.MultipleObjectsReturned as exception:
      raise DbObjectTwinException(object_type = 'Job', object_id = id_message.id) from exception


class Job(models.Model):
  """Job definition"""
  job_id      = models.TextField(default = 'UNKNOWN', unique = True)
  name        = models.TextField(default = 'UNKNOWN', unique = True)
  description = models.TextField()

  # Common configuration.
  cron_expression = models.TextField()
  action          = models.TextField(default = 'UNKNOWN')
  timelimit       = models.DurationField(default = timedelta(hours = 1))
  batch_size      = models.IntegerField(default = 1000)

  # Cleanup.
  is_cleanup_job  = models.BooleanField(default = False)
  cleanup_delay   = models.DurationField(default = timedelta())

  objects = JobManager()
