"""Utility for saving job configuration."""

# Python.
from datetime import timedelta

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import JobActionConfiguration, JobCleanupActionConfiguration


class JobConfigurationMixin(models.Model):
  """Mixin for job configuration."""

  # Action configuration.
  actionTimelimit = models.DurationField(default = timedelta(hours = 1))
  actionBatchSize = models.IntegerField(default = 1000)

  # Cleanup configuration.
  cleanupIs    = models.BooleanField(default = False)
  cleanupDelay = models.DurationField(default = timedelta())

  class Meta:
    abstract = True

  def jobConfigurationFromGrpc(
      self, *,
      action : JobActionConfiguration,
      cleanup: JobCleanupActionConfiguration,
  ) -> None :
    """Change own values according to the grpc object."""
    # Action configuration.
    self.actionBatchSize = action.batchSize if action.batchSize else 1000
    self.actionTimelimit = action.timelimit.ToTimedelta() \
      if action.timelimit.ToNanoseconds() > 0 else timedelta(hours = 1)

    # Cleanup configuration.
    self.cleanupIs    = cleanup.isCleanupJob
    self.cleanupDelay = cleanup.cleanupDelay.ToTimedelta()

  def jobConfigurationToGrpc(
      self, *,
      action : JobActionConfiguration,
      cleanup: JobCleanupActionConfiguration,
  ) -> None :
    """Return a grpc object containing own values."""
    # Action configuration.
    action.batchSize = self.actionBatchSize
    action.timelimit.FromTimedelta(self.actionTimelimit)

    # Cleanup configuration.
    cleanup.isCleanupJob = self.cleanupIs
    cleanup.cleanupDelay.FromTimedelta(self.cleanupDelay)
