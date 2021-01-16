"""Gracefully import settings."""

# Python.
from typing import cast

# Django.
from django.conf import settings


class Settings:
  """Group the auth settings."""

  # noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences
  settings = settings.KHALEESI_NINJA['BASE']  # type: ignore[index]

  @classmethod
  def max_failed_attempts(cls) -> int :
    """The number of failed login attempts before a user gets system locked."""
    return cast(int, cls.settings['MAX_FAILED_LOGIN_ATTEMPTS'])


class UserNames:
  """Group the auth user name settings."""

  # noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences
  names = settings.KHALEESI_NINJA['BASE']['USERS']  # type: ignore[index]

  @classmethod
  def anonymous(cls) -> str :
    """The username used for the anonymous user."""
    return cast(str, cls.names['ANONYMOUS'])

  @classmethod
  def superuser(cls) -> str :
    """The username used for the superuser."""
    return cast(str, cls.names['SUPERUSER'])
