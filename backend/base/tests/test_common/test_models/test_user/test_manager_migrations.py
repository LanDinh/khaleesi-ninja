"""The tests for the custom User."""

# Python.
from typing import cast
from unittest.mock import call, MagicMock, patch

# khaleesi.ninja.
from common.exceptions import TwinException
from common.models import User
from settings.settings import UserNames
from test_util.test import SimpleTestCase, TestCase
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class UserManagerUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom UserManager."""

  def test_create_anonymous_user_creation(self) -> None :
    """Test if the anonymous user gets created correctly."""
    with patch.object(User.migrations, 'get_queryset', return_value = MagicMock()) as queryset:
      with patch.object(User.migrations, 'model') as model:
        # Prepare data.
        user = self.create_anonymous_user()
        queryset.return_value.filter = MagicMock(return_value = [])
        model.return_value = user
        # Perform test.
        User.migrations.create_anonymous_user()
        # Assert result.
        self.assert_mocks(user = user)

  def test_create_anonymous_user_fetching(self) -> None :
    """Test if the anonymous user gets detected correctly."""
    with patch.object(User.migrations, 'get_queryset', return_value = MagicMock()) as queryset:
      # Prepare data.
      user = self.create_anonymous_user()
      queryset.return_value.filter = MagicMock(return_value = [user])
      # Perform test.
      User.migrations.create_anonymous_user()
      # Assert result.
      user.save.assert_not_called()  # type: ignore[attr-defined]

  def test_create_anonymous_twins(self) -> None :
    """Test if the anonymous user gets detected correctly."""
    with patch.object(User.migrations, 'get_queryset', return_value = MagicMock()) as queryset:
      # Prepare data.
      user = self.create_anonymous_user()
      queryset.return_value.filter = MagicMock(return_value = [user, user])
      # Perform test.
      with self.assertRaises(TwinException):
        User.migrations.create_anonymous_user()

  def test_create_superuser_creation(self) -> None :
    """Test if the anonymous user gets created correctly."""
    with patch.object(User.migrations, 'get_queryset', return_value = MagicMock()) as queryset:
      with patch.object(User.migrations, 'model') as model:
        # Prepare data.
        user = self.create_superuser()
        queryset.return_value.filter = MagicMock(return_value = [])
        model.return_value = user
        # Perform test.
        User.migrations.create_superuser()
        # Assert result.
        self.assert_mocks(user = user)

  def test_create_superuser_fetching(self) -> None :
    """Test if the anonymous user gets detected correctly."""
    with patch.object(User.migrations, 'get_queryset', return_value = MagicMock()) as queryset:
      # Prepare data.
      user = self.create_superuser()
      queryset.return_value.filter = MagicMock(return_value = [user])
      # Perform test.
      User.migrations.create_superuser()
      # Assert result.
      user.save.assert_not_called()  # type: ignore[attr-defined]

  def test_create_superuser_twins(self) -> None :
    """Test if the anonymous user gets detected correctly."""
    with patch.object(User.migrations, 'get_queryset', return_value = MagicMock()) as queryset:
      # Prepare data.
      user = self.create_superuser()
      queryset.return_value.filter = MagicMock(return_value = [user, user])
      # Perform test.
      with self.assertRaises(TwinException):
        User.migrations.create_superuser()

  @staticmethod
  def assert_mocks(*, user: User) -> None :
    """Correctly assert mock behavior."""
    cast(MagicMock, user).assert_has_calls([
        call.set_unusable_password(),
        call.full_clean(),
        call.save(),
    ])


# noinspection PyMethodMayBeStatic
class UserManagerIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom UserManager."""

  def test_create_anonymous_user(self) -> None :  # pylint: disable=no-self-use
    """Test if the anonymous user gets detected correctly."""
    # Assert that the user has been created beforehand.
    User.objects.get(username = UserNames.anonymous())
    # Assert there is no error when trying to create it again.
    User.migrations.create_anonymous_user()
    # Assert that no new anonymous user has been added.
    User.objects.get(username = UserNames.anonymous())

  def test_create_superuser(self) -> None :  # pylint: disable=no-self-use
    """Test if the superuser gets detected correctly."""
    # Assert that the user has been created beforehand.
    User.objects.get(username = UserNames.superuser())
    # Assert there is no error when trying to create it again.
    User.migrations.create_superuser()
    # Assert that no new superuser has been added.
    User.objects.get(username = UserNames.superuser())
