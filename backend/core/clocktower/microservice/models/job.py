"""Job definitions."""

# Python.
from __future__ import annotations
from datetime import timedelta
from typing import List
from uuid import uuid4

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parse_util import parse_string
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob


class JobManager(models.Manager['Job']):
  """Custom model manager."""

  def create_job(self, *, grpc_job: GrpcJob) -> Job :
    """Create a new job."""
    errors: List[str] = []

    batch_size = grpc_job.action_configuration.batch_size \
      if grpc_job.action_configuration.batch_size else 1000

    return self.create(
      job_id          = str(uuid4()),
      name            = parse_string(raw = grpc_job.name, name = 'name', errors = errors),
      description     = grpc_job.description,
      cron_expression = grpc_job.cron_expression,
      cleanup_delay   = grpc_job.cleanup_configuration.cleanup_delay.ToTimedelta(),
      timelimit       = grpc_job.action_configuration.timelimit.ToTimedelta(),
      batch_size      = batch_size,
      action          = parse_string(raw = grpc_job.action, name = 'action', errors = errors),
    )


class Job(models.Model):
  """Job definition"""
  job_id      = models.TextField(default = 'UNKNOWN')
  name        = models.TextField(default = 'UNKNOWN')
  description = models.TextField()

  # Common configuration.
  cron_expression = models.TextField()
  cleanup_delay   = models.DurationField(default = timedelta())
  timelimit       = models.DurationField(default = timedelta(hours = 1))
  batch_size      = models.IntegerField(default = 1000)
  action          = models.TextField(default = 'UNKNOWN')

  objects = JobManager()
