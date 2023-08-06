"""Test only models."""

from __future__ import annotations

# khaleesi.ninja.
from khaleesi.core.batch.jobConfigurationMixin import JobConfigurationMixin
from khaleesi.core.models.baseModel import Manager


class JobConfiguration(JobConfigurationMixin):
  """For testing the job configuration mixin."""

  objects: Manager[JobConfiguration] = Manager()
