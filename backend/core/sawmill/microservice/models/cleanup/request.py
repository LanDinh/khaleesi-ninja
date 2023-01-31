"""Request logs."""

# Django.
from django.db.models import QuerySet

# khaleesi.ninja.
from khaleesi.core.shared.job import CleanupJob
from microservice.models import Request


class RequestCleanupJob(CleanupJob[Request]):
  """Clean up requests."""

  def __init__(self) -> None :
    """Initialize job."""
    super().__init__(model = Request)

  def get_queryset(self) -> QuerySet[Request] :
    """Count the total number of items that should be executed."""
    return Request.objects.filter(meta_logged_timestamp__lt = self.cleanup_timestamp)
