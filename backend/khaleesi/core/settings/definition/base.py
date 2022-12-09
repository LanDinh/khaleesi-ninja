"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict

# khaleesi.ninja.
from khaleesi.core.settings.definition.grpc import Grpc
from khaleesi.core.settings.definition.metadata import Metadata
from khaleesi.core.settings.definition.monitoring import Monitoring


class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""

  METADATA   : Metadata
  GRPC       : Grpc
  MONITORING : Monitoring
