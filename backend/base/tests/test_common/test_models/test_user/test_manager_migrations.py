"""The tests for the custom User."""

# Python.
from unittest.mock import call, MagicMock, patch

# khaleesi.ninja.
from common.exceptions import TwinException
from common.models import User
from test_util.test import SimpleTestCase, TestCase
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin


class UserManagerUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom UserManager."""

  @patch.object(User.migrations, '_get_queryset')
  @patch.object(User.migrations, 'model')
  def test_create_anonymous_user_creation(
      self,
      model: MagicMock,
      queryset: MagicMock,
  ) -> None :
    """Test if the anonymous user gets created correctly."""
    # Prepare data.
    _, expected_user = self.create_anonymous_user()
    queryset.return_value.filter = MagicMock(return_value = [])
    model.return_value = expected_user
    mock = MagicMock()
    mock.set_password = expected_user.set_password
    mock.set_unusable_password = expected_user.set_unusable_password
    mock.full_clean = expected_user.full_clean
    mock.save = expected_user.save
    # Perform test.
    User.migrations.create_anonymous_user()
    # Assert result.
    mock.assert_has_calls([
        call.set_unusable_password(),
        call.full_clean(),
        call.save(),
    ])
    mock.set_password.assert_not_called()  # type: ignore[attr-defined]

  @patch.object(User.migrations, '_get_queryset')
  def test_create_anonymous_user_fetching(self, queryset: MagicMock) -> None :
    """Test if the anonymous user gets detected correctly."""
    # Prepare data.
    _, expected_user = self.create_anonymous_user()
    queryset.return_value.filter = MagicMock(return_value = [expected_user])
    # Perform test.
    User.migrations.create_anonymous_user()
    # Assert result.
    expected_user.save.assert_not_called()  # type: ignore[attr-defined]

  @patch.object(User.migrations, '_get_queryset')
  def test_create_anonymous_twins(self, queryset: MagicMock) -> None :
    """Test if the anonymous user gets detected correctly."""
    # Prepare data.
    _, expected_user = self.create_anonymous_user()
    queryset.return_value.filter = MagicMock(return_value = [expected_user, expected_user])
    # Perform test.
    with self.assertRaises(TwinException):
      User.migrations.create_anonymous_user()


class UserManagerIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom UserManager."""

  # noinspection PyMethodMayBeStatic
  def test_create_anonymous_user(self) -> None :  # pylint: disable=no-self-use
    """Test if the anonymous user gets detected correctly."""
    # Assert that the user has been created beforehand.
    # Assert there is no error when trying to create it again.
    User.migrations.create_anonymous_user()
    # Assert that no new anonymous user has been added.
    User.objects.get_anonymous_user()
