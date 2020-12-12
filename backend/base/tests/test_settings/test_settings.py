"""Test if settings can be read correctly."""

# Django.
from datetime import timedelta

from settings.settings import Settings
from test_util.test import CombinedTestCase


class SettingsTests(CombinedTestCase):
  """The combined tests for the Settings."""

  def test_dragon_groupname(self) -> None :
    """Make sure the admin group name gets read correctly."""
    dragon_groupname = Settings.dragon_groupname()
    self.assertTrue(isinstance(dragon_groupname, str))

  def test_missandei_groupname(self) -> None :
    """Make sure the translator group name gets read correctly."""
    missandei_groupname = Settings.missandei_groupname()
    self.assertTrue(isinstance(missandei_groupname, str))

  def test_warg_groupname(self) -> None :
    """Make sure the beta group name gets read correctly."""
    warg_groupname = Settings.warg_groupname()
    self.assertTrue(isinstance(warg_groupname, str))

  def test_permission_model(self) -> None :
    """Make sure the permission model gets read correctly."""
    permission_model = Settings.permission_model()
    self.assertTrue(isinstance(permission_model, str))

  def test_anonymous_username(self) -> None :
    """Make sure the anonymous username gets read correctly."""
    anonymous_username = Settings.anonymous_username()
    self.assertTrue(isinstance(anonymous_username, str))

  def test_khaleesi_username(self) -> None :
    """Make sure the khaleesi username gets read correctly."""
    khaleesi_username = Settings.khaleesi_username()
    self.assertTrue(isinstance(khaleesi_username, str))

  def test_system_lock_time(self) -> None :
    """Make sure the system lock time gets read correctly."""
    system_lock_time = Settings.system_lock_time()
    self.assertTrue(isinstance(system_lock_time, timedelta))

  def test_max_failed_attempts(self) -> None :
    """Make sure the max failed attempts get read correctly."""
    max_failed_attempt = Settings.max_failed_attempts()
    self.assertTrue(isinstance(max_failed_attempt, int))
