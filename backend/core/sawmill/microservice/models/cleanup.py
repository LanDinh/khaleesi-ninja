"""Base cleanup job."""

# Python.
from typing import TypeVar, Generic, cast

# Django.
from django.db.models import QuerySet

# khaleesi.ninja.
from khaleesi.core.batch.job import CleanupJob as BaseCleanupJob
from microservice.models.logs.abstract import Metadata


L = TypeVar('L', bound = Metadata)


class CleanupJob(BaseCleanupJob[L], Generic[L]):
  """Clean up requests."""

  def getQueryset(self) -> QuerySet[L] :
    """Count the total number of items that should be executed."""
    return cast(
      QuerySet[L],
      self.model.objects.filter(
        metaLoggedTimestamp__lt = self.request.cleanupConfiguration.cleanupDelay,
      ),
    )
