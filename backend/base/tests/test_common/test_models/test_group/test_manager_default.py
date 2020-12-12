"""The tests for the custom Group DefaultManager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import Manager, Group
from common.exceptions import ZeroTupletException
from test_util.test import SimpleTestCase, TestCase


class GroupDefaultManagerUnitTests(SimpleTestCase):
  """The unit tests for the custom Group DefaultManager."""

  @patch.object(Manager, 'get', return_value = MagicMock())
  def test_get(self, get: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if single object fetching works."""
    # Perform test.
    Group.objects.get(label = "label", name = "name")
    # Assert result.
    get.assert_called_once_with(name = 'label.name')



class GroupDefaultManagerIntegrationTests(TestCase):
  """The integration tests for the custom Group DefaultManager."""

  def test_get_zerotuplet(self) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    # Perform test.
    with self.assertRaises(ZeroTupletException):
      Group.objects.get(label = 'totally impossible label', name = 'totally impossible name')

  def test_get(self) -> None :
    """Test if single object fetching works."""
    # Prepare data.
    label = 'test'
    name = 'name'
    Group.base.create_group(label = label, name = name)
    # Perform test.
    result: Group = Group.objects.get(label = label, name = name)
    # Assert result.
    self.assertEqual(result.name, f'{label}.{name}')
