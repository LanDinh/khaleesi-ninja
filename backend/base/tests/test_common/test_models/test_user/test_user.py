"""The tests for the custom User."""

# Python.
from dataclasses import asdict
from datetime import timedelta
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from common.models import User
from settings.settings import Settings
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


class UserUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom User."""

  @patch.object(Settings, 'system_lock_time')
  def test_is_state(self, system_lock_time: MagicMock) -> None :
    """Test the state information getters."""
    system_lock_time.return_value = timedelta(minutes = 3)
    for username in ['username', Settings.anonymous_username()]:
      for params in self.params():
        is_authenticated = not username is Settings.anonymous_username()
        is_active = not params.locks.system_locked and not params.locks.admin_locked
        with self.subTest(authenticated = is_authenticated, **asdict(params)):
          # Prepare data.
          params.creates.username = username
          # Perform test.
          user, _ = self.create_user(params = params)
          # Assert result.
          self.assertEqual(is_authenticated, user.is_authenticated)
          self.assertEqual(is_active, user.is_active)
          self.assertEqual(params.locks.alias, user.is_alias())
          self.assertEqual(params.creates.oauth, user.is_oauth_only())
          self.assertEqual(params.locks.admin_locked, user.is_admin_locked())
          self.assertEqual(params.locks.system_locked, user.is_system_locked())
          # noinspection PyUnresolvedReferences
          user.save.assert_not_called()  # type: ignore[attr-defined]


class UserIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom User."""

  def test_is_state_authenticated(self) -> None :
    """Test the state information getters."""
    for params in self.params():
      is_active = not params.locks.system_locked and not params.locks.admin_locked
      with self.subTest(**asdict(params)):
        # Prepare data & perform test.
        user, _ = self.create_user(params = params)
        # Assert result.
        self.assertTrue(user.is_authenticated)
        self.assertEqual(is_active, user.is_active)
        self.assertEqual(params.locks.alias, user.is_alias())
        self.assertEqual(params.creates.oauth, user.is_oauth_only())
        self.assertEqual(params.locks.admin_locked, user.is_admin_locked())
        self.assertEqual(params.locks.system_locked, user.is_system_locked())
        user.delete()

  def test_is_state_anonymous(self) -> None :
    """Test the state information getters."""
    # Prepare data & perform test.
    User.migrations.create_anonymous_user()
    user: User = User.objects.get(username = Settings.anonymous_username())
    # Assert result.
    self.assertFalse(user.is_authenticated)
    self.assertFalse(user.is_alias())
    self.assertTrue(user.is_oauth_only())
    self.assertFalse(user.is_admin_locked())
    self.assertFalse(user.is_system_locked())
