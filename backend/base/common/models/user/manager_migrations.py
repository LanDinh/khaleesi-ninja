"""Manager specific for migrations."""

# Python.
from datetime import datetime

# khaleesi.ninja.
from common.models.manager import Manager
from common.exceptions import ZeroTupletException
from settings.settings import UserNames


class MigrationManager(Manager):
  """Manager specific for migrations."""

  def create_anonymous_user(self) -> None :
    """Create the one and only anonymous user."""
    self._create(raw_username = UserNames.anonymous())

  def create_superuser(self) -> None :
    """Create a new superuser."""
    self._create(raw_username = UserNames.superuser())

  def _create(self, *, raw_username: str) -> None :
    username = self.model.normalize_username(username = raw_username)
    try:
      self.get(username = username)
    except ZeroTupletException:
      #Only if the user doesn't exist yet, create it.
      user = self.model(username = username)
      user.date_joined = datetime.min
      user.last_activity = datetime.min
      user.set_unusable_password()
      user.full_clean()
      user.save()
