"""Default Manager."""

# Python.
from typing import cast, Optional

# khaleesi.ninja.
from ..manager import Manager, T


class DefaultManager(Manager):
  """Default Manager."""

  def get(self, *, username: str) -> T :
    """Get a single user by name."""
    return cast(T, super().get(username = username))

  def create_user(
      self, *,
      username: str,
      password: Optional[str] = None,
  ) -> T :
    """Create a new user."""
    return self._create_authenticated_user(
        username = username,
        password = password,
        is_superuser = False,
    )

  def create_superuser(
      self, *,
      username: str,
      password: Optional[str] = None,
  ) -> T :
    """Create a new superuser."""
    return self._create_authenticated_user(
        username = username,
        password = password,
        is_superuser = True,
    )

  def _create_authenticated_user(
      self, *,
      is_superuser: bool,
      username: str,
      password: Optional[str] = None,
  ) -> T :
    """Create a new user-like object."""
    user = self.model(
        username = self.model.normalize_username(username),
        is_superuser = is_superuser,
    )
    if password is None:
      user.set_unusable_password()
    else:
      user.set_password(raw_password = password)
    user.full_clean()
    user.save()
    return cast(T, user)
