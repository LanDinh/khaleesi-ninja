"""The tests for the custom role DefaultManager."""

# pylint: disable=line-too-long

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import Manager, Feature
from common.exceptions import ZeroTupletException
from common.service_type import ServiceType
from test_util.test import SimpleTestCase, TestCase


class FeatureDefaultManagerUnitTests(SimpleTestCase):
  """The unit tests for the custom role DefaultManager."""

  @patch.object(Manager, 'get', return_value = MagicMock())
  def test_get(self, get: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if single object fetching works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        # Perform test.
        Feature.objects.get(service = service, name = name)
        # Assert result.
        get.assert_called_once_with(service = service.name, name = name)
        get.reset_mock()

  @patch.object(Manager, 'get')
  @patch.object(Manager, 'get_queryset', return_value = MagicMock())
  def test_create_exists(self, base_queryset: MagicMock, get: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if single object creation works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        # Perform test.
        Feature.objects.create(service = service, name = name)
        # Assert result.
        get.assert_called_once_with(service = service.name, name = name)
        base_queryset.assert_not_called()
        get.reset_mock()

  @patch.object(Manager, 'get', side_effect = ZeroTupletException())
  @patch.object(Manager, 'get_queryset', return_value = MagicMock())
  def test_create_create(self, base_queryset: MagicMock, get: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if single object creation works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        # Perform test.
        Feature.objects.create(service = service, name = name)
        # Assert result.
        get.assert_called_once_with(service = service.name, name = name)
        base_queryset.return_value.create.assert_called_once_with(service = service.name, name = name)
        get.reset_mock()
        base_queryset.reset_mock()


class FeatureDefaultManagerIntegrationTests(TestCase):
  """The integration tests for the custom role DefaultManager."""

  def test_get_zerotuplet(self) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Perform test.
        with self.assertRaises(ZeroTupletException):
          Feature.objects.get(service = service, name = 'The cake is a lie!')

  def test_get(self) -> None :
    """Test if single object fetching works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        Feature.objects.create(service = service, name = name)
        # Perform test.
        result: Feature = Feature.objects.get(service = service, name = name)
        # Assert result.
        self.assertEqual(result.service, service.name)
        self.assertEqual(result.name, name)

  def test_create(self) -> None :
    """Test if single object fetching works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        # Perform test.
        Feature.objects.create(service = service, name = name)
        # Assert result.
        result: Feature = Feature.objects.get(service = service, name = name)
        self.assertEqual(result.service, service.name)
        self.assertEqual(result.name, name)
