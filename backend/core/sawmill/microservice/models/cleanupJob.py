"""Base cleanup job."""

# Python.
from typing import TypeVar, Generic, cast

# Django.
from django.db.models import QuerySet

# khaleesi.ninja.
from khaleesi.core.batch.job import CleanupJob as BaseCleanupJob
from microservice.models.logs.metadataMixin import MetadataMixin


Log = TypeVar('Log', bound = MetadataMixin)


class CleanupJob(BaseCleanupJob[Log], Generic[Log]):
  """Clean up requests."""

  def getQueryset(self) -> QuerySet[Log] :
    """Count the total number of items that should be executed."""
    return cast(
      QuerySet[Log],
      self.model.objects.filter(
        metaLoggedTimestamp__lt = self.request.configuration.cleanup.cleanupDelay,
      ),
    )
