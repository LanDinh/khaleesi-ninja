"""The tests for the custom User."""

# pylint: disable=line-too-long

# Python.
from dataclasses import asdict
from typing import List, cast
from unittest.mock import MagicMock

# khaleesi.ninja.
from common.models import User, Role, RoleAssignment
from common.models.auth.feature.feature_state import FeatureState
from common.service_type import ServiceType
from settings.settings import UserNames
from test_util.models.user import (
    TestUserUnitMixin,
    TestUserIntegrationMixin,
    Parameters,
)
from test_util.test import SimpleTestCase, TestCase


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class UserUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom User."""

  def test_is_authenticated(self) -> None :
    """Test if the user is authenticated."""
    for params in self.params():
      with self.subTest(**asdict(params)):
        # Perform test.
        user = self.create_user(params = params)
        # Assert result.
        self.assertTrue(user.is_authenticated)
        user.save.assert_not_called()  # type: ignore[attr-defined]

  def test_is_anonymous(self) -> None :
    """Test if the user is not authenticated."""
    for params in self.params():
      with self.subTest(**asdict(params)):
        # Prepare data.
        params.creates.username = ''
        # Perform test.
        user = self.create_user(params = params)
        # Assert result.
        self.assertFalse(user.is_authenticated)
        user.save.assert_not_called()  # type: ignore[attr-defined]

  def test_is_active(self) -> None :
    """Test if the user is active."""
    for params in self.params_active_only():
      with self.subTest(**asdict(params)):
        # Perform test.
        user = self.create_user(params = params)
        # Assert result.
        self.assertTrue(user.is_active)
        user.save.assert_not_called()  # type: ignore[attr-defined]

  def test_is_inactive(self) -> None :
    """Test if the user is inactive."""
    for params in self.params_inactive_only():
      with self.subTest(**asdict(params)):
        # Perform test.
        user = self.create_user(params = params)
        # Assert result.
        self.assertFalse(user.is_active)
        user.save.assert_not_called()  # type: ignore[attr-defined]

  def test_is_system_locked(self) -> None :
    """Test if the user is system locked."""
    # Prepare data.
    params = Parameters()
    params.locks.system_locked = True
    user = self.create_user(params = params)
    # Perform test.
    result = user.system_locked
    # Assert result
    self.assertTrue(result)
    user.save.assert_not_called()  # type: ignore[attr-defined]

  def test_is_not_system_locked(self) -> None :
    """Test if the user is not system locked."""
    # Prepare data.
    user = self.create_user(params = Parameters())
    # Perform test.
    result = user.system_locked
    # Assert result
    self.assertFalse(result)
    user.save.assert_not_called()  # type: ignore[attr-defined]

  def create_user(self, *, params: Parameters) -> User :
    """Create a unit test user according to requirements, mock super methods."""
    user = User(username = params.creates.username)
    user = self._attach_common_properties(mock = cast(MagicMock, user), params = params)
    return user


class UserIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom User."""

  def test_is_authenticated(self) -> None :
    """Test if the user is authenticated."""
    for params in self.params():
      with self.subTest(**asdict(params)):
        # Prepare data & perform test.
        user = self.create_user(params = params)
        # Assert result.
        self.assertTrue(user.is_authenticated)
        user.delete()

  def test_is_anonymous(self) -> None :
    """Test if the user is not authenticated."""
    # Prepare data & perform test.
    user = User.objects.get(username = UserNames.anonymous())
    # Assert result.
    self.assertFalse(user.is_authenticated)
    self.assertTrue(user.is_active)
    self.assertFalse(user.system_locked)
    self.assertFalse(user.has_usable_password())

  def test_is_active(self) -> None :
    """Test if the user is active."""
    for params in self.params_active_only():
      with self.subTest(**asdict(params)):
        # Prepare data & perform test.
        user = self.create_user(params = params)
        # Assert result.
        self.assertTrue(user.is_active)
        user.delete()

  def test_is_inactive(self) -> None :
    """Test if the user is not active."""
    for params in self.params_inactive_only():
      with self.subTest(**asdict(params)):
        # Prepare data & perform test.
        user = self.create_user(params = params)
        # Assert result.
        self.assertFalse(user.is_active)
        user.delete()

  def test_is_system_locked(self) -> None :
    """Test if the user is system locked."""
    # Prepare data.
    params = Parameters()
    params.locks.system_locked = True
    user = self.create_user(params = params)
    # Perform test.
    result = user.system_locked
    # Assert result
    self.assertTrue(result)

  def test_is_not_system_locked(self) -> None :
    """Test if the user is not system locked."""
    # Prepare data.
    user = self.create_user(params = Parameters())
    # Perform test.
    result = user.system_locked
    # Assert result
    self.assertFalse(result)

  def test_has_permission_inactive(self) -> None :
    """Test if permission handling works correctly."""
    for service in ServiceType:
      modes = ['not', 'regular', 'beta']
      roles = self.setup_role_and_features(service = service, modes = modes)
      for params in self.params_inactive_only():
        # Prepare data.
        user = self.create_user(params = params)
        self.setup_role_assignments(user = user, roles = roles)
        for mode in modes:
          for feature_state in FeatureState:
            with self.subTest(
                service = service,
                mode = mode,
                feature_state = feature_state,
                **asdict(params),
            ):
              # Perform test.
              result = user.has_permission(service = service, name = f'{mode}_{feature_state.name}')
              # Assert result.
              self.assertFalse(result)
        self.cleanup_user(user = user)

  def test_has_permission_active(self) -> None :
    """Test if permission handling works correctly."""
    for service in ServiceType:
      modes = ['not', 'regular', 'beta']
      roles = self.setup_role_and_features(service = service, modes = modes)
      for params in self.params_active_only():
        # Prepare data.
        user = self.create_user(params = params)
        self.setup_role_assignments(user = user, roles = roles)
        for mode, feature_state, expected in [
            (modes[0], FeatureState.BETA, False),
            (modes[0], FeatureState.RELEASED, False),
            (modes[0], FeatureState.LOCKED, False),
            (modes[1], FeatureState.BETA, False),
            (modes[1], FeatureState.RELEASED, True),
            (modes[1], FeatureState.LOCKED, False),
            (modes[2], FeatureState.BETA, True),
            (modes[2], FeatureState.RELEASED, True),
            (modes[2], FeatureState.LOCKED, False),
        ]:
          with self.subTest(
              service = service,
              mode = mode,
              feature_state = feature_state,
              **asdict(params),
          ):
            # Perform test.
            result = user.has_permission(service = service, name = f'{mode}_{feature_state.name}')
            # Assert result.
            self.assertEqual(expected, result)
        self.cleanup_user(user = user)

  @staticmethod
  def setup_role_and_features(*, service: ServiceType, modes: List[str]) -> List[Role] :
    """Setup the features for the permission tests."""
    roles = []
    for index, mode in enumerate(modes):
      Role.migrations.create(service = service, name = mode)
      roles.append(Role.objects.get(service = service.name, name = mode))
      for state in FeatureState:
        feature, _ = roles[index].features.get_or_create(
            service = service,
            name = f'{mode}_{state.name}',
        )
        feature.state = state.name
        feature.save()
    return roles

  def setup_role_assignments(self, *, user: User, roles: List[Role]) -> None :
    """Setup the roles and features for the permission tests."""
    self.assertEqual(3, len(roles))
    # Role assignments.
    RoleAssignment.objects.get_or_create(user = user, role = roles[1])
    beta_assignment, _ = RoleAssignment.objects.get_or_create(user = user, role = roles[2])
    beta_assignment.beta = True
    beta_assignment.save()

  @staticmethod
  def cleanup_user(*, user: User) -> None:
    """Delete the role including all associated features."""
    for role_assignment in user.roleassignment_set.all():
      role_assignment.delete()
    user.delete()
