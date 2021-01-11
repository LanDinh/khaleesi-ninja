"""Default Manager."""

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.service_type import ServiceType


# noinspection PyTypeHints,SyntaxError
class DefaultManager(Manager[T]):
  """Default Manager."""

  def get_or_create(self, *, service: ServiceType, name: str) -> T :  # type: ignore[override]
    """Create a feature."""
    feature, _ = self.get_queryset().get_or_create(service = service.name, name = name)
    return feature
