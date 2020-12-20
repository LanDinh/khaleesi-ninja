"""Test if settings can be read correctly."""

# Django.
from datetime import timedelta

from settings.settings import Settings, UserNames
from test_util.test import CombinedTestCase


class SettingsTests(CombinedTestCase):
  """The combined tests for the Settings."""

  def test_permission_model(self) -> None :
    """Make sure the permission model gets read correctly."""
    permission_model = Settings.permission_model()
    self.assertTrue(isinstance(permission_model, str))

  def test_system_lock_time(self) -> None :
    """Make sure the system lock time gets read correctly."""
    system_lock_time = Settings.system_lock_time()
    self.assertTrue(isinstance(system_lock_time, timedelta))

  def test_max_failed_attempts(self) -> None :
    """Make sure the max failed attempts get read correctly."""
    max_failed_attempt = Settings.max_failed_attempts()
    self.assertTrue(isinstance(max_failed_attempt, int))


class UserNamesTests(CombinedTestCase):
  """The combined tests for the Settings."""

  def test_anonymous(self) -> None :
    """Make sure the anonymous username gets read correctly."""
    name = UserNames.anonymous()
    self.assertTrue(isinstance(name, str))

  def test_superuser(self) -> None :
    """Make sure the khaleesi username gets read correctly."""
    name = UserNames.superuser()
    self.assertTrue(isinstance(name, str))

  def test_initial_superuser_password(self) -> None :
    """Make sure the initial superuser password gets read correctly."""
    name = UserNames.initial_superuser_password()
    self.assertTrue(isinstance(name, str))
