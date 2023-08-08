"""Test only models."""

from __future__ import annotations

# khaleesi.ninja.
from khaleesi.core.batch.jobExecutionMixin import JobExecutionMixin
from khaleesi.core.models.baseModel import Manager


class JobExecution(JobExecutionMixin):
  """For testing the job configuration mixin."""

  objects: Manager[JobExecution]
