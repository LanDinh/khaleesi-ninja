"""Manager specific for migrations."""

# khaleesi.ninja.
from common.models.manager import Manager, T
from common.exceptions import ZeroTupletException
from settings.settings import UserNames


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class MigrationManager(Manager[T]):
  """Manager specific for migrations."""

  def create_anonymous_user(self) -> None :
    """Create the one and only anonymous user."""
    self._create(raw_username = UserNames.anonymous())

  def create_superuser(self) -> None :
    """Create a new superuser."""
    self._create(raw_username = UserNames.superuser())

  def _create(self, *, raw_username: str) -> None :
    username = self.model.normalize_username(username = raw_username)  # type: ignore[attr-defined]
    try:
      self.get(username = username)
    except ZeroTupletException:
      #Only if the user doesn't exist yet, create it.
      user = self.model(username = username)
      user.set_unusable_password()  # type: ignore[attr-defined]
      user.full_clean()
      user.save()
