"""Gracefully import settings."""

# Python.
from datetime import timedelta
from typing import cast

# Django.
from django.conf import settings


class Settings:
  """Group the auth settings."""

  settings = settings.KHALEESI_NINJA['BASE']  # type: ignore[index]

  @classmethod
  def permission_model(cls) -> str :
    """The model name used for permission content types."""
    return cast(str, cls.settings['PERMISSION_MODEL'])

  @classmethod
  def system_lock_time(cls) -> timedelta :
    """The time in minutes that a system lock lasts."""
    return cast(timedelta, cls.settings['SYSTEM_LOCK_TIME'])

  @classmethod
  def max_failed_attempts(cls) -> int :
    """The number of failed login attempts before a user gets system locked."""
    return cast(int, cls.settings['MAX_FAILED_LOGIN_ATTEMPTS'])


class UserNames:
  """Group the auth user name settings."""

  names = settings.KHALEESI_NINJA['BASE']['USERS']  # type: ignore[index]

  @classmethod
  def anonymous(cls) -> str :
    """The username used for the anonymous user."""
    return cast(str, cls.names['ANONYMOUS'])

  @classmethod
  def superuser(cls) -> str :
    """The username used for the superuser."""
    return cast(str, cls.names['SUPERUSER'])

  @classmethod
  def initial_superuser_password(cls) -> str :
    """The initial password used for the superadmin."""
    return cast(str, cls.names['INITIAL_SUPERUSER_PASSWORD'])
