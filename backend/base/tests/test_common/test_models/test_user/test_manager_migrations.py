"""The tests for the custom User."""

# Python.
from datetime import datetime
from unittest.mock import call, MagicMock, patch

# khaleesi.ninja.
from settings.settings import Settings
from test_util.test import SimpleTestCase, TestCase
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin
from common.models import User


class UserManagerUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom UserManager."""

  @patch.object(User.migrations, '_get_queryset')
  @patch.object(User.migrations, 'model')
  def test_get_or_create_anonymous_user_creation(
      self,
      model: MagicMock,
      queryset: MagicMock,
  ) -> None :
    """Test if the anonymous user gets created correctly."""
    # Prepare data.
    _, expected_user = self.create_anonymous_user()
    queryset.return_value.filter = MagicMock(return_value = [])
    model.return_value = expected_user
    mock = self.setup_mocks(user = expected_user)
    # Perform test.
    user: User = User.migrations.get_or_create_anonymous_user()
    # Assert result.
    self.assert_mocks(mock = mock)
    self.assert_user(expected_user = expected_user, user = user)

  @patch.object(User.migrations, '_get_queryset')
  def test_get_or_create_anonymous_user_fetching(self, queryset: MagicMock) -> None :
    """Test if the anonymous user gets detected correctly."""
    # Prepare data.
    _, expected_user = self.create_anonymous_user()
    queryset.return_value.filter = MagicMock(return_value = [expected_user])
    # Perform test.
    user: User = User.migrations.get_or_create_anonymous_user()
    # Assert result.
    self.assert_user(expected_user = expected_user, user = user)
    # noinspection PyUnresolvedReferences
    user.save.assert_not_called()  # type: ignore[attr-defined]

  @staticmethod
  def setup_mocks(*, user: User) -> MagicMock :
    """Correctly prepare the mocks for mock assertion."""
    mock = MagicMock()
    mock.set_password = user.set_password
    mock.set_unusable_password = user.set_unusable_password
    mock.full_clean = user.full_clean
    mock.save = user.save
    return mock

  @staticmethod
  def assert_mocks(*, mock: MagicMock) -> None :
    """Assert that the mocks get called the way they should."""
    mock.assert_has_calls([
        call.set_unusable_password(),
        call.full_clean(),
        call.save(),
    ])
    mock.set_password.assert_not_called()


class UserManagerIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom UserManager."""

  def test_get_or_create_anonymous_user(self) -> None :
    """Test if the anonymous user gets detected correctly."""
    # Assert that the user has been created beforehand.
    self.assertEqual(0, len(User._objects.all()))  # pylint: disable=protected-access
    # Assert there is no error when trying to create it again.
    user: User = User.migrations.get_or_create_anonymous_user()
    # Assert that no new user has been added.
    self.assertEqual(1, len(User._objects.all()))  # pylint: disable=protected-access
    self.assert_anonymous_user(user = user)

  def assert_anonymous_user(self, *, user: User) -> None :
    """Assert user all attributes are correct."""
    # Assert the common attributes.
    self.assertEqual(Settings.anonymous_username(), user.username)
    self.assertFalse(user.has_usable_password())
    self.assertFalse(user.is_superuser)
    self.assertFalse(user.is_authenticated)
    self.assertTrue(user.is_active)
    self.assertEqual(datetime.min, user.date_joined)
    self.assertEqual(datetime.min, user.last_activity)
    # Assert the locked state attributes.
    self.assertEqual(None, user.original)
    self.assertFalse(user.admin_locked)
    self.assertEqual(datetime.min, user.system_locked)
