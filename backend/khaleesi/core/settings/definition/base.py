"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict

# khaleesi.ninja.
from khaleesi.core.settings.definition.batch import Batch
from khaleesi.core.settings.definition.grpc import Grpc
from khaleesi.core.settings.definition.metadata import Metadata
from khaleesi.core.settings.definition.monitoring import Monitoring
from khaleesi.core.settings.definition.singleton import Singletons
from khaleesi.core.settings.definition.startup import Startup


class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""

  METADATA   : Metadata
  GRPC       : Grpc
  MONITORING : Monitoring
  STARTUP    : Startup  # Required migrations before entering regular startup flow.
  BATCH      : Batch
  SINGLETONS : Singletons
