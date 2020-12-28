"""Test the custom base manager."""

# Python.
from unittest.mock import patch, MagicMock

# Django.
from django.db.models.manager import BaseManager as DjangoBaseManager

# khaleesi.ninja.
from common.models.manager import BaseManager
from common.exceptions import ZeroTupletException, TwinException
from test_util.test import SimpleTestCase
from .models import TestModel


# noinspection PyMethodMayBeStatic
class ManagerTestCase(SimpleTestCase):
  """Unit tests for the custom base manager."""

  @patch.object(BaseManager, '_get_queryset', return_value = MagicMock())
  def test_get_zerotuplet(self, get_queryset: MagicMock) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    # Prepare data.
    get_queryset.return_value.filter = MagicMock(return_value = [])
    # Perform test.
    with self.assertRaises(ZeroTupletException):
      TestModel.objects.get()

  @patch.object(BaseManager, '_get_queryset', return_value = MagicMock())
  def test_get_twins(self, get_queryset: MagicMock) -> None :
    """Test if the correct exception gets thrown if two objects are found."""
    # Prepare data.
    get_queryset.return_value.filter = MagicMock(return_value = ["", ""])
    # Perform test.
    with self.assertRaises(TwinException):
      TestModel.objects.get()

  @patch.object(BaseManager, '_get_queryset', return_value = MagicMock())
  def test_get(self, get_queryset: MagicMock) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    # Prepare data.
    expected = ""
    get_queryset.return_value.filter = MagicMock(return_value = [expected])
    # Perform test.
    result = TestModel.objects.get()
    # Assert result.
    self.assertEqual(expected, result)

  def test__get_queryset_forward_descriptors(self) -> None :  # pylint: disable=no-self-use
    """Test if the _get_queryset method works as intended."""
    # Prepare data.
    field = MagicMock()
    setattr(TestModel.objects, 'field', field)
    # Perform test.
    TestModel.objects._get_queryset()  # pylint: disable=protected-access
    # Assert result.
    field.remote_field.model._base_manager.db_manager.assert_called_once()  # pylint: disable=protected-access
    delattr(TestModel.objects, 'field')

  def test__get_queryset_reverse_descriptors(self) -> None :  # pylint: disable=no-self-use
    """Test if the _get_queryset method works as intended."""
    # Prepare data.
    related = MagicMock()
    setattr(TestModel.objects, 'related', related)
    # Perform test.
    TestModel.objects._get_queryset()  # pylint: disable=protected-access
    # Assert result.
    related.related_model._base_manager.db_manager.assert_called_once()  # pylint: disable=protected-access
    delattr(TestModel.objects, 'related')

  def test__get_queryset_many_descriptors_instance(self) -> None :  # pylint: disable=no-self-use
    """Test if the _get_queryset method works as intended."""
    # Prepare data.
    instance = MagicMock()
    setattr(TestModel.objects, 'instance', instance)
    setattr(TestModel.objects, 'prefetch_cache_name', 'test')
    # Perform test.
    TestModel.objects._get_queryset()  # pylint: disable=protected-access
    # Assert result.
    # It's not possible to mock a dict-like property.
    delattr(TestModel.objects, 'instance')
    delattr(TestModel.objects, 'prefetch_cache_name')

  @patch.object(DjangoBaseManager, 'get_queryset', return_value = MagicMock())
  def test__get_queryset_many_descriptors_fallback(self, base_manager: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if the _get_queryset method works as intended."""
    # Prepare data.
    filters = MagicMock()
    setattr(TestModel.objects, '_apply_rel_filters', filters)
    # Perform test.
    TestModel.objects._get_queryset()  # pylint: disable=protected-access
    # Assert result.
    base_manager.assert_called_once_with()
    filters.assert_called_once()
    delattr(TestModel.objects, '_apply_rel_filters')

  @patch.object(DjangoBaseManager, 'get_queryset', return_value = MagicMock())
  def test__get_queryset_regular_manager(self, base_manager: MagicMock) -> None :  # pylint: disable=no-self-use
    """Test if the _get_queryset method works as intended."""
    # Perform test.
    TestModel.objects._get_queryset()  # pylint: disable=protected-access
    # Assert result.
    base_manager.assert_called_once_with()
