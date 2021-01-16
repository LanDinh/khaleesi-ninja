"""Test if settings can be read correctly."""

# khaleesi.ninja.
from settings.settings import Settings, UserNames
from test_util.test import CombinedTestCase


class SettingsTests(CombinedTestCase):
  """The combined tests for the Settings."""

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
