"""Utility for saving job configuration."""

# Python.
from datetime import timedelta, datetime

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import JobConfiguration, Action


class JobConfigurationMixin(models.Model):
  """Mixin for job configuration."""
  # Target configuration.
  site    = models.TextField(default = 'UNKNOWN')
  app     = models.TextField(default = 'UNKNOWN')
  action  = models.TextField(default = 'UNKNOWN')

  # Action configuration.
  actionTimelimit = models.DurationField(default = timedelta(hours = 1))
  actionBatchSize = models.IntegerField(default = 1000)

  # Cleanup configuration.
  cleanupIs    = models.BooleanField(default = False)
  cleanupSince = models.DateTimeField(default = datetime.now)

  class Meta:
    abstract = True

  def jobConfigurationFromGrpc(self, *, action: Action, configuration: JobConfiguration) -> None :
    """Change own values according to the grpc object."""
    # Target configuration.
    self.site   = action.site
    self.app    = action.app
    self.action = action.action

    # Action configuration.
    self.actionBatchSize = configuration.action.batchSize \
      if configuration.action.batchSize else 1000
    self.actionTimelimit = configuration.action.timelimit.ToTimedelta() \
      if configuration.action.timelimit.ToNanoseconds() > 0 else timedelta(hours = 1)

    # Cleanup configuration.
    self.cleanupIs    = configuration.cleanup.isCleanupJob
    self.cleanupSince = configuration.cleanup.cleanupSince.ToDatetime()

  def jobConfigurationToGrpc(self, *, action: Action, configuration: JobConfiguration) -> None :
    """Return a grpc object containing own values."""
    # Target configuration.
    action.site   = self.site
    action.app    = self.app
    action.action = self.action

    # Action configuration.
    configuration.action.batchSize = self.actionBatchSize
    configuration.action.timelimit.FromTimedelta(self.actionTimelimit)

    # Cleanup configuration.
    configuration.cleanup.isCleanupJob = self.cleanupIs
    configuration.cleanup.cleanupSince.FromDatetime(self.cleanupSince)
