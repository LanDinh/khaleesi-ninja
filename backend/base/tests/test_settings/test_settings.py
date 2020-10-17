"""Test if settings can be read correctly."""

# Django.
from settings.settings import Settings
from test_util.test import CombinedTestCase


class SettingsTests(CombinedTestCase):
  """The combined tests for the Settings."""

  def test_anonymous_suffix(self) -> None :
    """Make sure the anonymous suffix gets read correctly."""
    anonymous_suffix = Settings.anonymous_suffix()
    self.assertTrue(isinstance(anonymous_suffix, str))

  def test_authenticated_suffix(self) -> None :
    """Make sure the authenticated suffix gets read correctly."""
    authenticated_suffix = Settings.authenticated_suffix()
    self.assertTrue(isinstance(authenticated_suffix, str))

  def test_dragon_suffix(self) -> None :
    """Make sure the dragon suffix gets read correctly."""
    dragon_suffix = Settings.dragon_suffix()
    self.assertTrue(isinstance(dragon_suffix, str))

  def test_permission_model(self) -> None :
    """Make sure the permission model gets read correctly."""
    permission_model = Settings.permission_model()
    self.assertTrue(isinstance(permission_model, str))

  def test_anonymous_username(self) -> None :
    """Make sure the anonymous username gets read correctly."""
    anonymous_username = Settings.anonymous_username()
    self.assertTrue(isinstance(anonymous_username, str))
