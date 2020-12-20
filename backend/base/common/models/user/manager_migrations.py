"""Manager specific for migrations."""

# Python.
from datetime import datetime
from typing import Optional

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
    self._create(
        raw_username = UserNames.superuser(),
        password = UserNames.initial_superuser_password()
    )

  def _create(self, *, raw_username: str, password: Optional[str] = None) -> None :
    username = self.model.normalize_username(username = raw_username)
    try:
      self.get(username = username)
    except ZeroTupletException:
      #Only if the user doesn't exist yet, create it.
      user = self.model(username = username)
      user.date_joined = datetime.min
      user.last_activity = datetime.min
      if password:
        user.set_password(raw_password = password)
      else:
        user.set_unusable_password()
      user.full_clean()
      user.save()
