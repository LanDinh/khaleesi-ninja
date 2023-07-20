"""Test only models."""

from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.batch.jobConfigurationMixin import JobConfigurationMixin


class JobConfiguration(JobConfigurationMixin):
  """For testing the job configuration mixin."""

  objects: models.Manager[JobConfiguration]
