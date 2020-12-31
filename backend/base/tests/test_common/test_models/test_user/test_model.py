"""The tests for the custom User."""

# pylint: disable=line-too-long

# Python.
from dataclasses import asdict
from datetime import timedelta
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from common.models import User, Role, Feature, FeatureAssignment, RoleAssignment
from common.models.feature_assignment.feature_assignment_state import \
  FeatureAssignmentState
from common.service_type import ServiceType
from settings.settings import UserNames, Settings
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class UserUnitTests(TestUserUnitMixin, SimpleTestCase):
  """The unit tests for the custom User."""

  @patch.object(Settings, 'system_lock_time')
  def test_is_state(self, system_lock_time: MagicMock) -> None :
    """Test the state information getters."""
    system_lock_time.return_value = timedelta(minutes = 3)
    for username in ['username', UserNames.anonymous()]:
      for params in self.params():
        is_authenticated = not username is UserNames.anonymous()
        is_active =\
          not params.locks.deleted\
          and not params.locks.admin_locked\
          and not params.locks.system_locked
        with self.subTest(authenticated = is_authenticated, **asdict(params)):
          # Prepare data.
          params.creates.username = username
          # Perform test.
          user, _ = self.create_user(params = params)
          # Assert result.
          self.assertEqual(is_authenticated, user.is_authenticated)
          self.assertEqual(is_active, user.is_active)
          self.assertEqual(params.locks.alias, user.is_alias())
          self.assertEqual(params.locks.admin_locked, user.is_admin_locked())
          self.assertEqual(params.locks.system_locked, user.is_system_locked())
          user.save.assert_not_called()  # type: ignore[attr-defined]


class UserIntegrationTests(TestUserIntegrationMixin, TestCase):
  """The integration tests for the custom User."""

  def test_is_state_authenticated(self) -> None :
    """Test the state information getters."""
    for params in self.params():
      is_active =\
        not params.locks.deleted\
        and not params.locks.admin_locked\
        and not params.locks.system_locked
      with self.subTest(**asdict(params)):
        # Prepare data & perform test.
        user, _ = self.create_user(params = params)
        # Assert result.
        self.assertTrue(user.is_authenticated)
        self.assertEqual(is_active, user.is_active)
        self.assertEqual(params.locks.alias, user.is_alias())
        self.assertEqual(params.locks.deleted, user.is_deleted())
        self.assertEqual(params.locks.admin_locked, user.is_admin_locked())
        self.assertEqual(params.locks.system_locked, user.is_system_locked())
        user.delete()

  def test_is_state_anonymous(self) -> None :
    """Test the state information getters."""
    # Prepare data & perform test.
    user: User = User.objects.get(username = UserNames.anonymous())
    # Assert result.
    self.assertFalse(user.is_authenticated)
    self.assertFalse(user.is_alias())
    self.assertFalse(user.has_usable_password())
    self.assertFalse(user.is_deleted())
    self.assertFalse(user.is_admin_locked())
    self.assertFalse(user.is_system_locked())

  def test_has_permission(self) -> None :
    """Test if permission handling works correctly."""
    for params in self.params():
      # Create user.
      user, _ = self.create_user(params = params)
      for service in ServiceType:
        # Prepare common data.
        modes = ['not', 'regular', 'beta']
        roles = []
        for mode in modes:
          roles.append(self.setup_role_and_features(service = service, name = mode))
        RoleAssignment.objects.get_or_create(user = user, role = roles[1])
        ass: RoleAssignment = RoleAssignment.objects.get(user = user, role = roles[2])
        ass.beta = True
        ass.save()
        for mode, state, expected in [
            (modes[0], FeatureAssignmentState.ALPHA, False),
            (modes[0], FeatureAssignmentState.BETA, False),
            (modes[0], FeatureAssignmentState.RELEASED, False),
            (modes[1], FeatureAssignmentState.ALPHA, True),
            (modes[1], FeatureAssignmentState.BETA, False),
            (modes[1], FeatureAssignmentState.RELEASED, True),
            (modes[2], FeatureAssignmentState.ALPHA, True),
            (modes[2], FeatureAssignmentState.BETA, True),
            (modes[2], FeatureAssignmentState.RELEASED, True),
        ]:
          with self.subTest(mode = mode, feature = state, service = service, user = params):
            # Perform test.
            result = user.has_permission(service = service, name = f'{mode}_{state.name}')
            # Assert result.
            self.assertEqual(expected, result)
        # Cleanup common data.
        for role in roles:
          self.cleanup_role_and_features(role = role)
      # Cleanup common data.
      user.delete()

  @staticmethod
  def setup_role_and_features(*, service: ServiceType, name: str) -> Role :
    """Setup the roles and features for the permission test."""
    Role.migrations.create(service = service, name = name)
    role: Role = Role.objects.get(service = service.name, name = name)
    for state in FeatureAssignmentState:
      feature: Feature = Feature.objects.get_or_create(service = service, name = f'{name}_{state.name}')
      FeatureAssignment.objects.create(role = role, feature = feature)
      ass: FeatureAssignment = FeatureAssignment.objects.get(role = role, feature = feature)
      ass.state = state.name
      ass.save()
    return role

  @staticmethod
  def cleanup_role_and_features(*, role: Role) -> None:
    """Delete the role including all associated features."""
    Feature.objects.get_queryset().filter(roles = role).delete()
    role.delete()
