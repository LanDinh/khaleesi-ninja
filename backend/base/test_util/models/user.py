"""Test utils for the User model."""

# pylint: disable=line-too-long

# Python.
import itertools
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Tuple, Callable, cast
from unittest.mock import MagicMock

# Django.
from django.utils import timezone

# khaleesi.ninja.
from common.models import User
from settings.settings import UserNames


@dataclass
class CreateParameters:
  """Parameters that need to be known at creation time."""
  username: str = 'username'

@dataclass
class LockParameters:
  """Parameters that will be adjusted after initial creation."""
  alias: bool = False
  deleted: bool = False
  admin_locked: bool = False
  system_locked: bool = False

@dataclass
class Parameters:
  """All parameters identifying a user."""
  creates: CreateParameters = CreateParameters()
  locks: LockParameters = LockParameters()


# noinspection PyTypeHints,PyUnresolvedReferences,SyntaxError,PyMissingOrEmptyDocstring,DuplicatedCode
class TestUserBaseMixin:
  """Test utils for the User model."""

  # Possible raw parameter values.
  _params_alias = [True, False]
  _params_deleted = [True, False]
  _params_admin_lock = [True, False]
  _params_system_lock = [True, False]

  def params_create(self) -> List[Parameters] :
    """Return parameter combinations for iteration in tests."""
    def filter_function(
        *,
        alias: bool,
        deleted: bool,
        admin_lock: bool,
        system_lock: bool,
        **_: bool,
    ) -> bool :
      return not alias and not deleted and not admin_lock and not system_lock
    return self._params_filtered(filter_function = filter_function)

  def params(self) -> List[Parameters] :
    """Return parameter combinations for iteration in tests."""
    def filter_function(**_: bool) -> bool :
      return True
    return self._params_filtered(filter_function = filter_function)

  def _params_filtered(self, *, filter_function: Callable) -> List[Parameters] :  # type: ignore[type-arg]
    """Return parameter combinations for iteration in tests."""
    return [
        Parameters(
            creates = CreateParameters(),
            locks = LockParameters(
                alias = alias,
                deleted = deleted,
                admin_locked = admin_locked,
                system_locked = system_locked,
            ),
        ) for alias, deleted, admin_locked, system_locked
        in itertools.product(
            self._params_alias,
            self._params_deleted,
            self._params_admin_lock,
            self._params_system_lock,
        )
        if filter_function(
            alias = alias,
            deleted = deleted,
            admin_lock = admin_locked,
            system_lock = system_locked,
        )
    ]

  @staticmethod
  def _add_properties_to_user(*, user: User, params: LockParameters) -> User:
    """Add lock properties to user."""
    user.original = user if params.alias else None
    user.deleted = params.deleted
    user.admin_locked = params.admin_locked
    user.failed_attempts = 1
    if params.system_locked:
      user.system_locked = timezone.now() - timedelta(microseconds = 1)
    return user

  def _assert_user(
      self, *,
      expected_user: User,
      user: User,
      new_system_lock: bool = False,
      new_activity: bool = False,
  ) -> None :
    """Assert that all User attributes are correct."""
    # Assert the common attributes of that user.
    self.assertEqual(expected_user.username, user.username)  # type: ignore[attr-defined]
    self.assertEqual(expected_user.is_authenticated, user.is_authenticated)  # type: ignore[attr-defined]
    self.assertEqual(expected_user.is_active, user.is_active)  # type: ignore[attr-defined]
    self.assertEqual(expected_user.date_joined, user.date_joined)  # type: ignore[attr-defined]
    if new_activity:
      self.assertNotEqual(expected_user.last_activity, user.last_activity)  # type: ignore[attr-defined]
    else:
      self.assertEqual(expected_user.last_activity, user.last_activity)  # type: ignore[attr-defined]
    # Assert the locked state attributes.
    if expected_user.original:
      self.assertEqual(expected_user.original.username, user.original.username)  # type: ignore[attr-defined,union-attr]
    else:
      self.assertEqual(expected_user.original, user.original)  # type: ignore[attr-defined]
    self.assertEqual(expected_user.deleted, user.deleted)  # type: ignore[attr-defined]
    self.assertEqual(expected_user.admin_locked, user.admin_locked)  # type: ignore[attr-defined]
    self.assertEqual(expected_user.failed_attempts, user.failed_attempts)  # type: ignore[attr-defined]
    if new_system_lock:
      self.assertNotEqual(expected_user.system_locked, user.system_locked)  # type: ignore[attr-defined]
    else:
      self.assertEqual(expected_user.system_locked, user.system_locked)  # type: ignore[attr-defined]


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class TestUserIntegrationMixin(TestUserBaseMixin):
  """Integration test specific test utils for the User model."""

  def create_user(self, *, params: Parameters) -> Tuple[User, User] :
    """Create a test user according to requirements."""
    user: User = User.objects.create(username = params.creates.username)
    user = self._add_properties_to_user(user = user, params = params.locks)
    user.save()
    return user, deepcopy(user)

  def assert_user(
      self, *,
      expected_user: User,
      new_system_lock: bool = False,
      new_activity: bool = False,
  ) -> None :
    """Assert User properties of the only User, then delete the User."""
    user: User = User.objects.get(username = expected_user.username)
    self._assert_user(
        expected_user = expected_user,
        user = user,
        new_system_lock = new_system_lock,
        new_activity = new_activity,
    )
    # Clean the database for other sub tests.
    user.delete()

  def assert_anonymous_user(self, *, user: User) -> None :
    """Assert user all attributes are correct."""
    # Assert the common attributes.
    self.assertEqual(UserNames.anonymous(), user.username)  # type: ignore[attr-defined]
    self.assertFalse(user.has_usable_password())  # type: ignore[attr-defined]
    self.assertFalse(user.is_authenticated)  # type: ignore[attr-defined]
    self.assertTrue(user.is_active)  # type: ignore[attr-defined]
    self.assertEqual(datetime.min, user.date_joined)  # type: ignore[attr-defined]
    self.assertEqual(datetime.min, user.last_activity)  # type: ignore[attr-defined]
    # Assert the locked state attributes.
    self.assertEqual(None, user.original)  # type: ignore[attr-defined]
    self.assertFalse(user.deleted)  # type: ignore[attr-defined]
    self.assertFalse(user.admin_locked)  # type: ignore[attr-defined]
    self.assertEqual(datetime.min, user.system_locked)  # type: ignore[attr-defined]

  def assert_superuser(self, *, user: User) -> None :
    """Assert user all attributes are correct."""
    # Assert the common attributes.
    self.assertEqual(UserNames.superuser(), user.username)  # type: ignore[attr-defined]
    self.assertTrue(user.has_usable_password())  # type: ignore[attr-defined]
    self.assertTrue(user.is_authenticated)  # type: ignore[attr-defined]
    self.assertTrue(user.is_active)  # type: ignore[attr-defined]
    self.assertEqual(datetime.min, user.date_joined)  # type: ignore[attr-defined]
    self.assertEqual(datetime.min, user.last_activity)  # type: ignore[attr-defined]
    # Assert the locked state attributes.
    self.assertIsNone(user.original)  # type: ignore[attr-defined]
    self.assertFalse(user.deleted)  # type: ignore[attr-defined]
    self.assertFalse(user.admin_locked)  # type: ignore[attr-defined]
    self.assertEqual(datetime.min, user.system_locked)  # type: ignore[attr-defined]


# noinspection PyUnresolvedReferences,PyTypeHints,PyMissingOrEmptyDocstring
class TestUserUnitMixin(TestUserBaseMixin):
  """Unit test specific test utils for the User model."""

  def create_user(self, *, params: Parameters) -> Tuple[User, User] :
    """Create a unit test user according to requirements, mock super methods."""
    user = User(username = params.creates.username)
    user = self._attach_common_properties(user = user, params = params)
    return user, deepcopy(user)

  def create_anonymous_user(self) -> Tuple[User, User] :
    """Create a unit user according to requirements, mock super methods."""
    params = Parameters()
    params.creates.username = UserNames.anonymous()
    user, _ = self.create_user(params = params)
    return user, deepcopy(user)

  def create_superuser(self) -> Tuple[User, User] :
    """Create a superuser according to requirements, mock super methods."""
    params = Parameters()
    params.creates.username = UserNames.superuser()
    user, _ = self.create_user(params = params)
    return user, deepcopy(user)


  def create_mock_user(self, *, params: Parameters) -> Tuple[MagicMock, MagicMock] :
    """Create a test user according to requirements, mock super methods."""
    mock = MagicMock()
    mock.username = params.creates.username
    mock = cast(MagicMock, self._attach_common_properties(user = cast(User, mock), params = params))
    return self._attach_mocks_to_user(mock = mock, params = params)

  def assert_user(
      self, *,
      expected_user: User,
      user: User,
      new_system_lock: bool = False,
      new_activity: bool = False,
  ) -> None :
    """Assert that all User attributes are correct."""
    self._assert_user(
        expected_user = expected_user,
        user = user,
        new_system_lock = new_system_lock,
        new_activity = new_activity,
    )

  def _attach_common_properties(
      self, *,
      user: User,
      params: Parameters,
  ) -> User :
    user = self._add_properties_to_user(user = user, params = params.locks)
    user.save = MagicMock()  # type: ignore[assignment]
    user.full_clean = MagicMock()  # type: ignore[assignment]
    user.set_unusable_password = MagicMock()  # type: ignore[assignment]
    user.has_usable_password = MagicMock(return_value = False)  # type: ignore[assignment]
    return user

  @staticmethod
  def _attach_mocks_to_user(
      *,
      mock: MagicMock,
      params: Parameters,
  ) -> Tuple[MagicMock, MagicMock] :
    """Create a unit test user according to requirements, mock all methods."""
    mock.date_joined = datetime.min
    mock.last_activity = datetime.min
    mock.system_locked = datetime.min
    mock.is_authenticated = MagicMock(bool(params.creates.username))
    mock.is_active = MagicMock(
        return_value =
            not params.locks.deleted
            and not params.locks.admin_locked
            and not params.locks.system_locked,
    )
    mock.is_alias = MagicMock(return_value = params.locks.alias)
    mock.is_deleted = MagicMock(return_value = params.locks.deleted)
    mock.is_admin_locked = MagicMock(return_value = params.locks.admin_locked)
    mock.is_system_locked = MagicMock(return_value = params.locks.system_locked)
    mock.roles = MagicMock()
    mock.roles.set = MagicMock()
    return mock, deepcopy(mock)
