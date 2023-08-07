"""khaleesi.ninja settings definition."""

# Python.
from enum import Enum
from typing import TypedDict


class AppType(Enum):
  """Types of khaleesi.ninja apps."""

  MICRO = 1

class Metadata(TypedDict):
  """Metadata for khaleesi.ninja apps."""

  SITE   : str
  APP    : str
  TYPE   : AppType
  VERSION: str
  POD_ID : str
