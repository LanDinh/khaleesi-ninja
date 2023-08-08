"""Test only models."""

from __future__ import annotations

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Manager
from microservice.models.jobConfigurationMixin import JobConfigurationMixin


class JobConfiguration(JobConfigurationMixin):
  """For testing the job configuration mixin."""

  objects: Manager[JobConfiguration]
