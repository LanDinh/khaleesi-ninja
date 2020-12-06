"""Manager specific for migrations."""

# Python.
from datetime import datetime
from typing import cast

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.exceptions import TwinException
from settings.settings import Settings


class MigrationManager(Manager):
  """Manager specific for migrations."""

  def get_or_create_anonymous_user(self) -> T :
    """Create the one and only anonymous user."""
    users = self._get_queryset().filter(username = Settings.anonymous_username())
    if users:
      if len(users) == 1:
        return cast(T, users[0])
      raise TwinException()
    user = self.model(username = Settings.anonymous_username())
    user.set_unusable_password()
    user.date_joined = datetime.min
    user.last_activity = datetime.min
    user.full_clean()
    user.save()
    return cast(T, user)
