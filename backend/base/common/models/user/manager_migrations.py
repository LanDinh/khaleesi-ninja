"""Manager specific for migrations."""

# Python.
from datetime import datetime

# khaleesi.ninja.
from common.models.manager import Manager
from common.exceptions import TwinException
from settings.settings import Settings


class MigrationManager(Manager):
  """Manager specific for migrations."""

  def create_anonymous_user(self) -> None :
    """Create the one and only anonymous user."""
    users = self._get_queryset().filter(username = Settings.anonymous_username())
    if users:
      if len(users) == 1:
        return
      raise TwinException()
    user = self.model(username = Settings.anonymous_username())
    user.set_unusable_password()
    user.date_joined = datetime.min
    user.last_activity = datetime.min
    user.full_clean()
    user.save()
    return
