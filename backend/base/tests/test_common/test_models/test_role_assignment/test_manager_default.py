"""The tests for the custom role assignment DefaultManager."""

# Python.
from dataclasses import asdict
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import Role, RoleAssignment, Manager
from common.service_type import ServiceType
from test_util.test import SimpleTestCase, TestCase
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin


class RoleAssignmentDefaultManagerUnitTests(SimpleTestCase, TestUserUnitMixin):
  """The unit tests for the custom role assignment DefaultManager."""

  @patch.object(Manager, '_get_queryset', return_value = MagicMock())
  def test_create(self, base_queryset: MagicMock) -> None :
    """Test role assignment creation."""
    for user_params in self.params():
      for service in ServiceType:
        with self.subTest(service = service, **asdict(user_params)):
          # Prepare data.
          base_queryset.return_value.create = MagicMock()
          user, _ = self.create_user(params = user_params)
          role = Role(service = service.name)
          # Perform test.
          RoleAssignment.objects.create(user = user, role = role)
          # Assert result.
          base_queryset.return_value.create.assert_called_once_with(user = user, role = role)


class RoleAssignmentDefaultManagerIntegrationTests(TestCase, TestUserIntegrationMixin):
  """The integration tests for the custom role assignment DefaultManager."""

  def test_create(self) -> None :
    """Test role assignment creation."""
    for user_params in self.params():
      for service in ServiceType:
        for role_name in ['', 'test']:
          with self.subTest(service = service, **asdict(user_params)):
            # Prepare data.
            user, _ = self.create_user(params = user_params)
            Role.migrations.create(service = service, name = role_name)
            role: Role = Role.objects.get(service = service, name = role_name)
            # Perform test.
            RoleAssignment.objects.create(user = user, role = role)
            # Assert result.
            result: RoleAssignment = user.roles.get(service = service, name = role_name)
            self.assertEqual(user, result.user)
            self.assertEqual(role, result.role)
            self.assertFalse(result.beta)
            user.delete()
            role.delete()
