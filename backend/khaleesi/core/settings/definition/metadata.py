"""khaleesi.ninja settings definition."""

# Python.
from enum import Enum
from typing import TypedDict


class ServiceType(Enum):
  """Types of khaleesi.ninja services."""

  MICRO = 1

class Metadata(TypedDict):
  """Metadata for khaleesi.ninja services."""

  GATE    : str
  SERVICE : str
  TYPE    : ServiceType
  VERSION : str
  POD_ID  : str
