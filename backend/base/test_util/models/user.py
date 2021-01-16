"""Test utils for the User model."""

# pylint: disable=line-too-long

# Python.
import itertools
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Callable, cast
from unittest.mock import MagicMock

# khaleesi.ninja.
from common.models import User
from settings.settings import UserNames, Settings


@dataclass
class CreateParameters:
  """Parameters that need to be known at creation time."""
  username: str = 'username'

@dataclass
class LockParameters:
  """Parameters that will be adjusted after initial creation."""
  deleted: bool = False
  admin_locked: bool = False
  system_locked: bool = False

@dataclass
class Parameters:
  """All parameters identifying a user."""
  creates: CreateParameters = field(default_factory = CreateParameters)
  locks: LockParameters = field(default_factory = LockParameters)


# noinspection PyTypeHints,PyUnresolvedReferences,SyntaxError,PyMissingOrEmptyDocstring,DuplicatedCode
class TestUserBaseMixin:
  """Test utils for the User model."""

  # Possible raw parameter values.
  _params_deleted = [True, False]
  _params_admin_lock = [True, False]
  _params_system_lock = [True, False]

  def params_active_only(self) -> List[Parameters] :
    """Return parameter combinations for iteration in tests."""
    def filter_function(deleted: bool, admin_locked: bool, system_locked: bool, **_: bool) -> bool :
      return not deleted and not admin_locked and not system_locked
    return self._params_filtered(filter_function = filter_function)

  def params_inactive_only(self) -> List[Parameters] :
    """Return parameter combinations for iteration in tests."""
    def filter_function(deleted: bool, admin_locked: bool, system_locked: bool, **_: bool) -> bool :
      return deleted or admin_locked or system_locked
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
                deleted = deleted,
                admin_locked = admin_locked,
                system_locked = system_locked,
            ),
        ) for deleted, admin_locked, system_locked
        in itertools.product(
            self._params_deleted,
            self._params_admin_lock,
            self._params_system_lock,
        )
        if filter_function(
            deleted = deleted,
            admin_locked = admin_locked,
            system_locked = system_locked,
        )
    ]

  @staticmethod
  def _add_properties_to_user(*, user: User, params: LockParameters) -> User:
    """Add lock properties to user."""
    user.deleted = params.deleted
    user.admin_locked = params.admin_locked
    if params.system_locked:
      user.failed_attempts = Settings.max_failed_attempts() + 1
    else:
      user.failed_attempts = 1
    return user


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class TestUserIntegrationMixin(TestUserBaseMixin):
  """Integration test specific test utils for the User model."""

  def create_user(self, *, params: Parameters) -> User :
    """Create a test user according to requirements."""
    user = User.objects.create(username = params.creates.username)
    user = self._add_properties_to_user(user = user, params = params.locks)
    user.save()
    return user


# noinspection PyUnresolvedReferences,PyTypeHints,PyMissingOrEmptyDocstring
class TestUserUnitMixin(TestUserBaseMixin):
  """Unit test specific test utils for the User model."""

  def create_user(self, *, params: Parameters) -> User :
    """Create a unit test user according to requirements, mock super methods."""
    mock = MagicMock()
    mock.username = params.creates.username
    self._attach_mocks_to_user(user = mock, params = params)
    self._attach_common_properties(mock = mock, params = params)
    return cast(User, mock)

  def create_anonymous_user(self) -> User :
    """Create a unit user according to requirements, mock super methods."""
    params = Parameters()
    params.creates.username = UserNames.anonymous()
    return self.create_user(params = params)

  def create_superuser(self) -> User :
    """Create a superuser according to requirements, mock super methods."""
    params = Parameters()
    params.creates.username = UserNames.superuser()
    return self.create_user(params = params)

  def _attach_common_properties(self, *, mock: MagicMock, params: Parameters) -> MagicMock :
    user = self._add_properties_to_user(user = cast(User, mock), params = params.locks)
    mock = cast(MagicMock, user)
    mock.save = MagicMock()
    mock.full_clean = MagicMock()
    mock.set_unusable_password = MagicMock()
    mock.has_usable_password = MagicMock(return_value = False)
    return mock

  @staticmethod
  def _attach_mocks_to_user(*, user: MagicMock, params: Parameters) -> MagicMock :
    """Create a unit test user according to requirements, mock all methods."""
    user.date_joined = datetime.min
    user.is_authenticated = bool(params.creates.username)
    user.is_active = \
      not params.locks.deleted\
      and not params.locks.admin_locked\
      and not params.locks.system_locked
    user.roles = MagicMock()
    user.roles.set = MagicMock()
    return user
