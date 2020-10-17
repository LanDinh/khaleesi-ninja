"""Gracefully import settings."""

# Python.
from typing import cast

# Django.
from django.conf import settings


class Settings:
  """Group the auth settings."""

  settings = settings.KHALEESI_NINJA['BASE']  # type: ignore[index]

  @classmethod
  def anonymous_suffix(cls) -> str :
    """The suffix for anonymous groups."""
    return cast(str, cls.settings['ANONYMOUS_SUFFIX'])

  @classmethod
  def authenticated_suffix(cls) -> str :
    """The suffix for authenticated groups."""
    return cast(str, cls.settings['AUTHENTICATED_SUFFIX'])

  @classmethod
  def dragon_suffix(cls) -> str :
    """The suffix for dragons."""
    return cast(str, cls.settings['DRAGON_SUFFIX'])

  @classmethod
  def permission_model(cls) -> str :
    """The model name used for permission content types."""
    return cast(str, cls.settings['PERMISSION_MODEL'])

  @classmethod
  def anonymous_username(cls) -> str :
    """The username used for the anonymous user."""
    return cast(str, cls.settings['ANONYMOUS_USERNAME'])
