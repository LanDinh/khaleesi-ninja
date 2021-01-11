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

  @patch.object(Manager, 'get_queryset', return_value = MagicMock())
  def test_create(self, base_queryset: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if single object creation works."""
    base_queryset.return_value.get_or_create.return_value = (MagicMock(), True)
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        # Perform test.
        Feature.objects.get_or_create(service = service, name = name)
        # Assert result.
        base_queryset.return_value.get_or_create.assert_called_once_with(service = service.name, name = name)
        base_queryset.reset_mock()


class FeatureDefaultManagerIntegrationTests(TestCase):
  """The integration tests for the custom role DefaultManager."""

  def test_get_zerotuplet(self) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Perform test.
        with self.assertRaises(ZeroTupletException):
          Feature.objects.get(service = service.name, name = 'The cake is a lie!')

  def test_create(self) -> None :
    """Test if single object fetching works."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        # Perform test.
        Feature.objects.get_or_create(service = service, name = name)
        # Assert result.
        result = Feature.objects.get(service = service.name, name = name)
        self.assertEqual(result.service, service.name)
        self.assertEqual(result.name, name)
