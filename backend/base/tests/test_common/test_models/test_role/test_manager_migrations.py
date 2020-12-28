"""The tests for the custom role MigrationManager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja
from common.exceptions import ZeroTupletException
from common.models import Role
from common.models.manager import BaseManager
from common.service_type import ServiceType
from test_util.test import  SimpleTestCase, TestCase


class RoleMigrationManagerUnitTests(SimpleTestCase):
  """The unit tests for the MigrationManager."""

  @patch.object(BaseManager, '_get_queryset', return_value = MagicMock())
  def create(self, base_queryset: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test role creation."""
    for service in ServiceType:
      for name in ['', 'test']:
        with self.subTest(service = service, name = name):
          # Prepare data.
          base_queryset.return_value.update_or_create = MagicMock()
          # Perform test.
          Role.migrations.create(service = service, name = name)
          # Assert result.
          base_queryset.return_value.update_or_create.assert_called_once_with(
              service = service,
              name = name,
          )


class RoleMigrationManagerIntegrationTests(TestCase):
  """The integration tests for the MigrationManager."""

  def test_create_again(self) -> None :
    """Test role creation."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        Role.objects.get(service = service)
        # Perform test.
        Role.migrations.create(service = service)
        # Assert result.
        Role.objects.get(service = service)

  def test_create_new(self) -> None :
    """Test role creation."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        with self.assertRaises(ZeroTupletException):
          Role.objects.get(service = service, name = name)
        # Perform test.
        Role.migrations.create(service = service, name = name)
        # Assert result.
        role: Role = Role.objects.get(service = service, name = name)
        self.assertFalse(role.authenticated)
