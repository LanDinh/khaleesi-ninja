"""Manager specific for migrations."""

# Python.
from datetime import datetime
from typing import Optional, cast

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.exceptions import ZeroTupletException
from settings.settings import UserNames


class MigrationManager(Manager):
  """Manager specific for migrations."""

  def create_anonymous_user(self) -> None :
    """Create the one and only anonymous user."""
    user = self._create_base_user(username = UserNames.anonymous())
    if user:
      user.set_unusable_password()
      user.full_clean()
      user.save()

  def create_superuser(self) -> None :
    """Create a new superuser."""
    user = self._create_base_user(username = UserNames.superuser())
    if user:
      user.is_superuser = True
      user.set_password(raw_password = UserNames.initial_superuser_password())
      user.full_clean()
      user.save()

  def _create_base_user(self, *, username: str) -> Optional[T] :
    username = self.model.normalize_username(username = username)
    try:
      self.get(username = username)
    except ZeroTupletException:
      #Only if the user doesn't exist yet, create it.
      user = self.model(username = username)
      user.date_joined = datetime.min
      user.last_activity = datetime.min
      return cast(T, user)
    return None
