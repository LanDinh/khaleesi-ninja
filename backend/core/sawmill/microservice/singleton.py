"""Per-request state."""

# Python.
import threading

# khaleesi.ninja.
from microservice.models import Request, BackgateRequest, Event, Error, Query
from microservice.models.cleanup import CleanupJob


class Singleton(threading.local):
  """Per-request state."""

  cleanup_backgate_requests: CleanupJob[BackgateRequest]
  cleanup_requests         : CleanupJob[Request]
  cleanup_events           : CleanupJob[Event]
  cleanup_errors           : CleanupJob[Error]
  cleanup_queries          : CleanupJob[Query]

  def __init__(self) -> None :
    """Set the default state."""
    super().__init__()
    self.cleanup_backgate_requests = CleanupJob(model = BackgateRequest)
    self.cleanup_requests          = CleanupJob(model = Request)
    self.cleanup_events            = CleanupJob(model = Event)
    self.cleanup_errors            = CleanupJob(model = Error)
    self.cleanup_queries           = CleanupJob(model = Query)


SINGLETON = Singleton()
