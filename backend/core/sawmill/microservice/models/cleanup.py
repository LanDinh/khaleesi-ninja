"""Base cleanup job."""

# Python.
from typing import TypeVar, Generic, cast

# Django.
from django.db.models import QuerySet

# khaleesi.ninja.
from khaleesi.core.shared.job import CleanupJob as BaseCleanupJob
from microservice.models.logs.abstract import Metadata


L = TypeVar('L', bound = Metadata)


class CleanupJob(BaseCleanupJob[L], Generic[L]):
  """Clean up requests."""

  def get_queryset(self) -> QuerySet[L] :
    """Count the total number of items that should be executed."""
    return cast(
      QuerySet[L],
      self.model.objects.filter(meta_logged_timestamp__lt = self.cleanup_timestamp),
    )
