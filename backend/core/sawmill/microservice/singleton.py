"""Per-request state."""

# Python.
import threading

# khaleesi.ninja.
from microservice.models.cleanup.request import RequestCleanupJob


class Singleton(threading.local):
  """Per-request state."""

  cleanup_requests: RequestCleanupJob

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.cleanup_requests = RequestCleanupJob()


SINGLETON = Singleton()
