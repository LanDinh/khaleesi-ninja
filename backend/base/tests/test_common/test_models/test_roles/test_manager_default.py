"""The tests for the custom role DefaultManager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import Manager, Role
from common.exceptions import ZeroTupletException
from common.service_type import ServiceType
from test_util.test import SimpleTestCase, TestCase


class RoleDefaultManagerUnitTests(SimpleTestCase):
  """The unit tests for the custom role DefaultManager."""

  @patch.object(Manager, 'get', return_value = MagicMock())
  def test_get(self, get: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if single object fetching works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        # Perform test.
        Role.objects.get(service = service, name = name)
        # Assert result.
        get.assert_called_once_with(service = service.name, name = name)
        get.reset_mock()


class RoleDefaultManagerIntegrationTests(TestCase):
  """The integration tests for the custom role DefaultManager."""

  def test_get_zerotuplet(self) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Perform test.
        with self.assertRaises(ZeroTupletException):
          Role.objects.get(service = service, name = 'The cake is a lie!')

  def test_get(self) -> None :
    """Test if single object fetching works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Perform test.
        result: Role = Role.objects.get(service = service)
        # Assert result.
        self.assertEqual(result.service, service.name)
        self.assertEqual(result.name, '')
