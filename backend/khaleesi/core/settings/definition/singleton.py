"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict


class Singleton(TypedDict):
  """Singleton fully qualified path."""

  NAME: str


class Singletons(TypedDict):
  """Singleton configuration for khaleesi.ninja apps."""

  STRUCTURED_LOGGER: Singleton
  BROOM            : Singleton
