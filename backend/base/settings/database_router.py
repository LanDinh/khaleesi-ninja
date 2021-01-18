"""Custom database router to enable a separate connection for logs."""

# pylint: disable=line-too-long

# Python.
from typing import Any, Optional

# Django.
from django.db.models import Model


# noinspection PyProtectedMember
class LoggingRouter:
  """Custom database router to enable a separate connection for logs."""

  database = 'logging'
  # noinspection SpellCheckingInspection
  relations = [('logrequest', 'user')]

  @staticmethod
  def app_label(*, model: Model) -> bool :
    """Check if the model is of the correct app."""
    return model._meta.app_label == 'common'  # pylint: disable=protected-access

  @staticmethod
  def model_prefix(*, model: Model) -> bool :
    """Check if the model name starts correctly."""
    if model._meta.model_name:  # pylint: disable=protected-access
      return model._meta.model_name.startswith('log')  # pylint: disable=protected-access
    return False

  def relation(self, *, obj1: Model, obj2: Model) -> bool :
    """Check if the relation between the objects is allowed."""
    for rel1, rel2 in self.relations:
      if obj1._meta.model_name == rel1 and obj2._meta.model_name == rel2:  # pylint: disable=protected-access
        return True
      if obj1._meta.model_name == rel2 and obj2._meta.model_name == rel1:  # pylint: disable=protected-access
        return True
    return False

  def db_for_read(self, model: Model, **_: Any) -> Optional[str] :
    """Enable for logging."""
    if self.app_label(model = model) and self.model_prefix(model = model):
      return self.database
    return None

  def db_for_write(self, model: Model, **_: Any) -> Optional[str] :
    """Enable for logging."""
    if self.app_label(model = model) and self.model_prefix(model = model):
      return self.database
    return None

  def allow_relation(self, obj1: Model, obj2: Model, **_: Any) -> Optional[bool] :
    """Enable for logging."""
    if self.app_label(model = obj1) and self.app_label(model = obj2):
      if self.relation(obj1 = obj1, obj2 = obj2):
        return True
    return None

  # noinspection PyUnusedLocal
  def allow_migrate(self, db: str, *args: Any, **kwargs: Any) -> Optional[bool] :  # pylint: disable=invalid-name,unused-argument
    """Enable for logging."""
    if db == self.database:
      return False
    return None
