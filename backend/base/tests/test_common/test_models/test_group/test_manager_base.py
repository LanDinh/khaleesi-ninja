"""The tests for the custom Group MigrationManager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja
from common.exceptions import ZeroTupletException
from common.models import Group
from common.models.manager import BaseManager
from test_util.models.group import TestGroupUnitMixin
from test_util.test import  SimpleTestCase, TestCase


class GroupBaseManagerUnitTests(SimpleTestCase, TestGroupUnitMixin):
  """The unit tests for the BaseManager."""

  @patch.object(BaseManager, '_get_queryset', return_value = MagicMock())
  def test_create_group(self, base_queryset: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test group creation."""
    # Prepare data.
    base_queryset.return_value.update_or_create = MagicMock()
    label = 'test'
    name = 'test'
    # Perform test.
    Group.base.create_group(label = label, name = name)
    # Assert result.
    base_queryset.return_value.update_or_create.assert_called_once_with(name = f'{label}.{name}')


class GroupBaseManagerIntegrationTests(TestCase):
  """The integration tests for the BaseManager."""

  def test_create_new_group(self) -> None :
    """Test group creation."""
    # Prepare data.
    label = 'test'
    name = 'test'
    with self.assertRaises(ZeroTupletException):
      Group.objects.get(label = label, name = name)
    # Perform test.
    Group.base.create_group(label = label, name = name)
    # Assert result.
    group: Group = Group.objects.get(label = label, name = name)
    self.assertFalse(group.authenticated)
    self.assertFalse(group.beta)
    self.assertFalse(group.translator)
    self.assertEqual(f'{label}.{name}', group.name)
