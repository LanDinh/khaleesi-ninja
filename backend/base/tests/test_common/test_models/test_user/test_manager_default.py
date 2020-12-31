"""The tests for the custom User."""

# Python.
from datetime import datetime
from typing import List
from unittest.mock import call, MagicMock, patch

# Django.
from django.core.exceptions import ValidationError

# khaleesi.ninja.
from common.models import User, Manager, Role, RoleAssignment
from common.exceptions import ZeroTupletException
from common.service_type import ServiceType
from settings.settings import UserNames
from test_util.test import SimpleTestCase, TestCase
from test_util.models.user import (
  TestUserUnitMixin,
  TestUserIntegrationMixin, Parameters,
)


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class UserManagerUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom UserManager."""

  @patch.object(Manager, 'get_queryset')
  def test_without_role_assignment(self, base_queryset: MagicMock) -> None :
    """Test if the users that are not assigned to a role get fetched correctly."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        base_queryset.return_value.filter = MagicMock()
        role = Role(service = service.name)
        # Perform test.
        User.objects.without_role_assignment(role = role)
        # Assert result.
        base_queryset.return_value.exclude.assert_called_once_with(roles = role)

  def test_create(self) -> None :
    """Test if user creation succeeds."""
    # Prepare data.
    params = Parameters()
    _, expected_user = self.create_user(params = params)
    User.objects.model = MagicMock(return_value = expected_user)
    mock = MagicMock()
    mock.set_unusable_password = expected_user.set_unusable_password
    mock.full_clean = expected_user.full_clean
    mock.save = expected_user.save
    # Perform test.
    user: User = User.objects.create(username = params.creates.username)
    # Assert result.
    self.assert_user(expected_user = expected_user, user = user)
    mock.assert_has_calls([
        call.set_unusable_password(),
        call.full_clean(),
        call.save(),
    ])


class UserManagerIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom UserManager."""

  def test_get_zerotuplet(self) -> None :
    """Test if gets behaves correctly."""
    # Perform test.
    with self.assertRaises(ZeroTupletException):
      User.objects.get(username = 'first of her name')

  def test_without_role_assignment(self) -> None :
    """Test if the users that are not assigned to a role get fetched correctly."""
    user_name1 = 'user1'
    user_name2 = 'user2'
    role_name = 'test'
    for params1 in self.params():
      params1.creates.username = user_name1
      for params2 in self.params():
        params2.creates.username = user_name2
        for service in ServiceType:
          # Prepare common data.
          user1, _ = self.create_user(params = params1)
          user2, _ = self.create_user(params = params2)
          Role.migrations.create(service = service, name = role_name)
          role: Role = Role.objects.get(service = service.name, name = role_name)
          with self.subTest(case = '0 users', service = service, user1 = params1, user2 = params2):
            # Perform test.
            result_no_user: List[User] = User.objects.without_role_assignment(role = role)
            # Assert result.
            self.assert_user_list(result = result_no_user, included = [user1, user2])
          with self.subTest(case = '1 user', service = service, user1 = params1, user2 = params2):
            # Prepare data.
            RoleAssignment.objects.get_or_create(user = user1, role = role)
            # Perform test.
            result_one_user: List[User] = User.objects.without_role_assignment(role = role)
            # Assert result.
            self.assert_user_list(result = result_one_user, included = [user2], excluded = [user1])
          with self.subTest(case = '2 users', service = service, user1 = params1, user2 = params2):
            # Prepare data.
            role.authenticated = True
            role.save()
            # Perform test.
            result_two_users: List[User] = User.objects.without_role_assignment(role = role)
            # Assert result.
            self.assert_user_list(result = result_two_users, excluded = [user1, user2])
          # Cleanup data.
          user1.delete()
          user2.delete()
          role.delete()

  def test_create(self) -> None :
    """Test if user creation succeeds."""
    # Prepare data.
    username = 'username'
    # Perform test.
    User.objects.create(username = username)
    # Assert result.
    self.assert_single_user_created(username = username)

  def test_create_username_failure(self) -> None :
    """Test if user creation fails."""
    for username, error in [
        ('/', 'Enter a valid username.'),
        ('a'*151, 'Ensure this value has at most 150 characters'),
    ]:
      with self.subTest(username = username):
        # Perform test.
        with self.assertRaisesRegex(ValidationError, error):
          User.objects.create(username = username)
        # Assert result.
        self.assert_no_save()

  def test_create_twin_failure(self) -> None :
    """Test if user creation succeeds."""
    # Prepare data.
    username = 'username'
    User.objects.create(username = username)
    twin = 'UsErNaMe'
    # Perform test.
    with self.assertRaisesRegex(ValidationError, 'User with this Username already exists.'):
      User.objects.create(username = twin)
    # Assert result.
    self.assert_single_user_created(username = username)

  # noinspection PyDefaultArgument
  def assert_user_list(  # pylint: disable=dangerous-default-value
      self, *,
      result: List[User],
      included: List[User] = [],
      excluded: List[User] = [],
  ) -> None :
    """Assert that the result list looks the way it is supposed to look."""
    result_names = {user.username for user in result}
    included_names = {user.username for user in included}
    excluded_names = {user.username for user in excluded}
    self.assertEqual(len(result), len(result_names))
    for user in included_names:
      self.assertTrue(user in result_names)
    for user in excluded_names:
      self.assertFalse(user in result_names)
    self.assertFalse(UserNames.anonymous() in result_names)

  def assert_single_user_created(self, *, username: str) -> None :
    """Assert user all attributes are correct, then clean up the database."""
    # Assert there is only one user.
    user: User = User.objects.get(username = username)
    # Assert the common attributes of that user.
    self.assertEqual(username, user.username)
    self.assertTrue(user.is_authenticated)
    self.assertTrue(user.is_active)
    self.assertNotEqual(datetime.min, user.date_joined)
    self.assertNotEqual(datetime.min, user.last_activity)
    # Assert the locked state attributes.
    self.assertEqual(None, user.original)
    self.assertFalse(user.admin_locked)
    self.assertEqual(0, user.failed_attempts)
    self.assertEqual(datetime.min, user.system_locked)
    # Assert the password behavior.
    self.assertFalse(user.has_usable_password())

  def assert_no_save(self) -> None :
    """Assert that no object was saved to the database."""
    self.assertEqual(2, len(User._objects.all()))  # pylint: disable=protected-access
