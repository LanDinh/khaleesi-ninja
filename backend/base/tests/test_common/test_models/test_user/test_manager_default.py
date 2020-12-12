"""The tests for the custom User."""

# Python.
from dataclasses import asdict
from datetime import datetime
from unittest.mock import call, MagicMock, patch

# Django.
from django.core.exceptions import ValidationError

# khaleesi.ninja.
from common.models import User, Manager
from common.exceptions import ZeroTupletException
from settings.settings import Settings
from test_util.test import SimpleTestCase, TestCase
from test_util.models.user import (
    CreateParameters,
    TestUserUnitMixin,
    TestUserIntegrationMixin,
)


class UserManagerUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom UserManager."""

  @patch.object(Manager, 'get')
  def test_get(self, get: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if gets behaves correctly."""
    # Perform test.
    User.objects.get(username = 'whatever')
    # Assert result.
    get.assert_called_once_with(username = 'whatever')

  @patch.object(Manager, 'get')
  def test_get_anonymous_user(self, get: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if gets behaves correctly."""
    # Perform test.
    User.objects.get_anonymous_user()
    # Assert result.
    get.assert_called_once_with(username = Settings.anonymous_username())

  def test_create_user_and_superuser(self) -> None :
    """Test if user creation succeeds."""
    for params in self.params_create():
      with self.subTest(**asdict(params)):
        # Prepare data.
        _, expected_user = self.create_user(params = params)
        User.objects.model = MagicMock(return_value = expected_user)
        mock = self.setup_mocks(user = expected_user)
        # Perform test.
        user = self.creation(superuser = params.creates.superuser)(
            username = params.creates.username,
            password = params.creates.password,
        )
        # Assert result.
        # noinspection PyTypeChecker
        self.assert_mocks(mock = mock, params = params.creates)
        self.assert_user(expected_user = expected_user, user = user)

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
  def assert_mocks(*, mock: MagicMock, params: CreateParameters) -> None :
    """Assert that the mocks get called the way they should."""
    if params.oauth:
      mock.assert_has_calls([
          call.set_unusable_password(),
          call.full_clean(),
          call.save(),
      ])
      mock.set_password.assert_not_called()
    else:
      mock.assert_has_calls([
          call.set_password(raw_password = params.password),
          call.full_clean(),
          call.save(),
      ])
      mock.set_unusable_password.assert_not_called()


class UserManagerIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom UserManager."""

  def test_get(self) -> None :
    """Test if gets behaves correctly."""
    # Perform test.
    with self.assertRaises(ZeroTupletException):
      User.objects.get(username = 'impossible username')

  def test_get_anonymous_user(self) -> None :
    """Test if gets behaves correctly."""
    # Prepare data.
    User.migrations.create_anonymous_user()
    # Perform test.
    user: User = User.objects.get(username = Settings.anonymous_username())
    # Assert result.
    self.assert_anonymous_user(user = user)

  def test_create_user_and_superuser(self) -> None :
    """Test if user creation succeeds."""
    for params in self.params_create():
      with self.subTest(**asdict(params)):
        # Perform test.
        self.creation(superuser = params.creates.superuser)(
            username = params.creates.username,
            password = params.creates.password,
        )
        # Assert result.
        self.assert_single_user_created(params = params.creates)

  def test_create_user_fails_for_username(self) -> None :
    """Test if creation fails based on username errors."""
    for username, error in [
        ('/', 'Enter a valid username.'),
        ('a'*151, 'Ensure this value has at most 150 characters'),
    ]:
      for params in self.params_create():
        # Prepare data.
        params.creates.username = username
        with self.subTest(**asdict(params)):
          # Perform test.
          with self.assertRaisesRegex(ValidationError, error):
            self.creation(superuser = params.creates.superuser)(
                username = params.creates.username,
                password = params.creates.password,
            )
          # Assert result.
          self.assert_no_save()

  def test_create_user_fails_for_twins(self) -> None :
    """Test that capitalization doesn't allow for twin creation."""
    error = 'User with this Username already exists.'
    for params in self.params_create():
      for twin_params in self.params_create():
        with self.subTest(params = params, twin_params = params):
          # Prepare data.
          self.creation(superuser = params.creates.superuser)(
              username = params.creates.username,
              password = params.creates.password,
          )
          twin_params.creates.username = params.creates.username.title()
          # Perform test.
          with self.assertRaisesRegex(ValidationError, error):
            User.objects.create_user(
                username = twin_params.creates.username,
                password = twin_params.creates.password,
            )
          with self.assertRaisesRegex(ValidationError, error):
            User.objects.create_superuser(
                username = twin_params.creates.username,
                password = twin_params.creates.password,
            )
          # Assert result.
          self.assert_single_user_created(params = params.creates)

  def assert_single_user_created(self, *, params: CreateParameters) -> None :
    """Assert user all attributes are correct, then clean up the database."""
    # Assert there is only one user.
    user: User = User.objects.get(username = params.username)
    # Assert the common attributes of that user.
    self.assertEqual(params.username, user.username)
    self.assertTrue(user.is_authenticated)
    self.assertTrue(user.is_active)
    self.assertNotEqual(datetime.min, user.date_joined)
    self.assertNotEqual(datetime.min, user.last_activity)
    self.assertEqual(params.superuser, user.is_superuser)
    # Assert the locked state attributes.
    self.assertEqual(None, user.original)
    self.assertFalse(user.admin_locked)
    self.assertEqual(0, user.failed_attempts)
    self.assertEqual(datetime.min, user.system_locked)
    # Assert the password behavior.
    self.assertEqual(not params.oauth, user.has_usable_password())
    self.assertNotEqual(params.password, user.password)
    # Clean the database for other sub tests.
    user.delete()

  def assert_no_save(self) -> None :
    """Assert that no object was saved to the database."""
    self.assertEqual(0, len(User._objects.all()))  # pylint: disable=protected-access
