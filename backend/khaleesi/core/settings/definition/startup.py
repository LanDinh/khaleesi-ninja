"""khaleesi.ninja settings definition."""

# Python.
from typing import TypedDict


class MigrationsBeforeServerStart(TypedDict):
  """Migrations that might need to be applied first."""
  REQUIRED : bool
  MIGRATION: str



class Startup(TypedDict):
  """Startup configuration for khaleesi.ninja services."""

  MIGRATIONS_BEFORE_SERVER_START: MigrationsBeforeServerStart
