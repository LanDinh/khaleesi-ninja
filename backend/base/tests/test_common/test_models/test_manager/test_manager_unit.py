"""Test the custom base manager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import Manager
from common.exceptions import ZeroTupletException, TwinException
from test_util.test import SimpleTestCase
from .models import TestModel


# noinspection PyMethodMayBeStatic
class ManagerTestCase(SimpleTestCase):
  """Unit tests for the custom base manager."""

  @patch.object(Manager, 'get_queryset', return_value = MagicMock())
  def test_get_zerotuplet(self, get_queryset: MagicMock) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    # Prepare data.
    get_queryset.return_value.filter = MagicMock(return_value = [])
    # Perform test.
    with self.assertRaises(ZeroTupletException):
      TestModel.objects.get()

  @patch.object(Manager, 'get_queryset', return_value = MagicMock())
  def test_get_twins(self, get_queryset: MagicMock) -> None :
    """Test if the correct exception gets thrown if two objects are found."""
    # Prepare data.
    get_queryset.return_value.filter = MagicMock(return_value = ["", ""])
    # Perform test.
    with self.assertRaises(TwinException):
      TestModel.objects.get()

  @patch.object(Manager, 'get_queryset', return_value = MagicMock())
  def test_get(self, get_queryset: MagicMock) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    # Prepare data.
    expected = ""
    get_queryset.return_value.filter = MagicMock(return_value = [expected])
    # Perform test.
    result = TestModel.objects.get()
    # Assert result.
    self.assertEqual(expected, result)
