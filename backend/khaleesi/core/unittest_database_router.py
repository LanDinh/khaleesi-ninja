"""Database router to distinguish between read and write operations."""

# Python.
from typing import Optional, Any

# khaleesi.ninja.
from .database_router import DatabaseRouter


class TestDatabaseRouter(DatabaseRouter):
  """Database router to distinguish between read and write operations."""

  def allow_migrate(
      self,
      db: str,
      _app_label: str,
      _model_name: Optional[str] = None,
      **_: Any
  ) -> bool :
    return 'write' == db