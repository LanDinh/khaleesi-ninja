"""Database router to distinguish between read and write operations."""

# Python.
from typing import Type, Optional, Any

# Django.
from django.db.models import Model


# noinspection PyMethodMayBeStatic
class DatabaseRouter:
  """Database router to distinguish between read and write operations."""

  def db_for_read(self, _model: Type[Model], **_: Any) -> str :  # pylint: disable=no-self-use
    """Return the database alias for reads."""
    return 'read'

  def db_for_write(self, _model: Type[Model], **_: Any) -> str :  # pylint: disable=no-self-use
    """Return the database alias for writes."""
    return 'write'

  def allow_migrate(
      self,
      db: str,
      _app_label: str,
      _model_name: Optional[str] = None,
      **_: Any
  ) -> bool :
    """Return the database alias for migrations."""  # pylint: disable=no-self-use,invalid-name
    return 'migrate' == db
