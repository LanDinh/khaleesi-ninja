"""Gracefully import settings."""

# Python.
from datetime import timedelta
from typing import cast

# Django.
from django.conf import settings


class Settings:
  """Group the auth settings."""

  settings = settings.KHALEESI_NINJA['BASE']  # type: ignore[index]
  groupnames = settings['GROUPNAMES']  # type: ignore[index]

  @classmethod
  def dragon_groupname(cls) -> str :
    """The group name used for admins."""
    return cast(str, cls.groupnames['DRAGON'])

  @classmethod
  def missandei_groupname(cls) -> str :
    """The group name used for translators."""
    return cast(str, cls.groupnames['MISSANDEI'])

  @classmethod
  def warg_groupname(cls) -> str :
    """The group name used for beta testers."""
    return cast(str, cls.groupnames['WARG'])

  @classmethod
  def permission_model(cls) -> str :
    """The model name used for permission content types."""
    return cast(str, cls.settings['PERMISSION_MODEL'])

  @classmethod
  def anonymous_username(cls) -> str :
    """The username used for the anonymous user."""
    return cast(str, cls.settings['ANONYMOUS_USERNAME'])

  @classmethod
  def system_lock_time(cls) -> timedelta :
    """The time in minutes that a system lock lasts."""
    return cast(timedelta, cls.settings['SYSTEM_LOCK_TIME'])

  @classmethod
  def max_failed_attempts(cls) -> int :
    """The number of failed login attempts before a user gets system locked."""
    return cast(int, cls.settings['MAX_FAILED_LOGIN_ATTEMPTS'])
