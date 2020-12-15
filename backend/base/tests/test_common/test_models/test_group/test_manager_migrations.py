"""The tests for the custom Group MigrationManager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja
from common.exceptions import ZeroTupletException
from common.models import Group
from common.models.manager import BaseManager
from settings.settings import Settings
from test_util.models.group import TestGroupUnitMixin
from test_util.test import  SimpleTestCase, TestCase


class GroupMigrationManagerUnitTests(SimpleTestCase, TestGroupUnitMixin):
  """The unit tests for the MigrationManager."""

  @patch.object(BaseManager, '_get_queryset', return_value = MagicMock())
  def test_create(self, base_queryset: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test group creation."""
    # Prepare data.
    base_queryset.return_value.update_or_create = MagicMock()
    name = 'test'
    # Perform test.
    Group.migrations.create(name = name)
    # Assert result.
    base_queryset.return_value.update_or_create.assert_called_once_with(name = name)


class GroupMigrationManagerIntegrationTests(TestCase):
  """The integration tests for the MigrationManager."""

  def test_create_new(self) -> None :
    """Test group creation."""
    # Prepare data.
    name = 'test'
    with self.assertRaises(ZeroTupletException):
      Group.objects.get(name = name)
    # Perform test.
    Group.migrations.create(name = name)
    # Assert result.
    group: Group = Group.objects.get(name = name)
    self.assertFalse(group.authenticated)
    self.assertFalse(group.beta)
    self.assertFalse(group.translator)
    self.assertEqual(name, group.name)

  def test_create_again(self) -> None :
    """Test group creation."""
    # Prepare data.
    Group.objects.get(name = Settings.dragon_groupname())
    # Perform test.
    Group.migrations.create(name = Settings.dragon_groupname())
    # Assert result.
    group: Group = Group.objects.get(name = Settings.dragon_groupname())
    self.assertFalse(group.authenticated)
    self.assertFalse(group.beta)
    self.assertFalse(group.translator)
    self.assertEqual(Settings.dragon_groupname(), group.name)
