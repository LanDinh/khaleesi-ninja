"""The tests for the signals assigning roles."""

# Python.
from dataclasses import asdict
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.exceptions import ZeroTupletException
from common.models import User, RoleAssignment, Role
from common.service_type import ServiceType
from common.signals.assign_roles import (
  assign_roles_when_creating_user,
  assign_roles_when_saving_role,
)
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class AssignRolesUnitTests(SimpleTestCase, TestUserUnitMixin):
  """The unit tests for the signals assigning roles."""

  def test_assign_roles_when_creating_user(self) -> None :
    """Test if roles get assigned upon user save."""
    with patch.object(RoleAssignment.objects, 'get_or_create') as create:
      with patch.object(Role.objects, 'authenticated', return_value = ['test']):
        for params in self.params():
          with self.subTest(**asdict(params)):
            # Prepare data.
            user = self.create_user(params = params)
            # Perform test.
            assign_roles_when_creating_user(instance = user, created = True)
            create.assert_called_once_with(user = user, role = 'test')
            create.reset_mock()

  @patch.object(RoleAssignment.objects, 'get_or_create')
  @patch.object(Role.objects, 'authenticated', return_value = ['test'])
  def test_assign_roles_when_creating_anonymous_user(
      self,
      _: MagicMock,
      create: MagicMock,
  ) -> None :
    """Test if roles get assigned upon user save."""
    # Prepare data.
    user = self.create_anonymous_user()
    # Perform test.
    assign_roles_when_creating_user(instance = user, created = True)
    create.assert_not_called()

  @patch.object(RoleAssignment.objects, 'get_or_create')
  @patch.object(Role.objects, 'authenticated', return_value = ['test'])
  def test_assign_roles_when_not_creating_user(self, _: MagicMock, create: MagicMock) -> None :
    """Test if roles get assigned upon user save."""
    for params in self.params():
      with self.subTest(**asdict(params)):
        # Prepare data.
        user = self.create_user(params = params)
        # Perform test.
        assign_roles_when_creating_user(instance = user, created = False)
        create  .assert_not_called()

  def test_assign_roles_when_saving_authenticated_role(self) -> None :
    """Test if roles get assigned upon role save."""
    with patch.object(RoleAssignment.objects, 'get_or_create') as create:
      with patch.object(User.objects, 'without_role_assignment', return_value = ['test']):
        for service in ServiceType:
          with self.subTest(service = service):
            # Prepare data.
            role = Role(service = service.name, authenticated = True)
            # Perform test.
            assign_roles_when_saving_role(instance = role)
            # Assert result.
            create.assert_called_once_with(user = 'test', role = role)


class AssignRolesIntegrationTests(TestCase, TestUserIntegrationMixin):
  """The integration tests for the signals assigning roles."""

  def test_assign_roles_when_creating_user(self) -> None :
    """Test if roles get assigned upon user save."""
    for params in self.params():
      for service in ServiceType:
        with self.subTest(service = service, **asdict(params)):
          # Prepare data.
          name = 'test'
          Role.migrations.create(service = service, name = name)
          role = Role.objects.get(service = service.name, name = name)
          role.authenticated = True
          role.save()
          # Perform test.
          user = self.create_user(params = params)
          # Assert result.
          user.roles.get(service = service.name, name = name)
          user.delete()
          role.delete()

  def test_assign_roles_when_saving_role_newly_authenticated(self) -> None :
    """Test if roles get assigned upon role save."""
    for params in self.params():
      for service in ServiceType:
        with self.subTest(service = service, **asdict(params)):
          # Prepare data.
          name = 'test'
          user = self.create_user(params = params)
          Role.migrations.create(service = service, name = name)
          role = Role.objects.get(service = service.name, name = name)
          with self.assertRaises(ZeroTupletException):
            user.roles.get(service = service, name = name)
          # Perform test.
          role.authenticated = True
          role.save()
          # Assert result.
          user.roles.get(service = service.name, name = name)
          user.delete()
          role.delete()

  def test_assign_roles_when_saving_role_newly_unauthenticated(self) -> None :
    """Test if roles get assigned upon role save."""
    for params in self.params():
      for service in ServiceType:
        with self.subTest(service = service, **asdict(params)):
          # Prepare data.
          name = 'test'
          user = self.create_user(params = params)
          Role.migrations.create(service = service, name = name)
          role = Role.objects.get(service = service.name, name = name)
          role.authenticated = True
          role.save()
          user.roles.get(service = service.name, name = name)
          # Perform test.
          role.authenticated = False
          role.save()
          # Assert result.
          with self.assertRaises(ZeroTupletException):
            user.roles.get(service = service, name = name)
          user.delete()
          role.delete()
