"""Test the custom base manager."""

# khaleesi.ninja.
from common.exceptions import ZeroTupletException, TwinException
from test_util.test import TestCase
from .models import TestModel


# noinspection PyUnresolvedReferences,PyArgumentList,PyMissingOrEmptyDocstring,PyCallingNonCallable
class ManagerTestCase(TestCase):
  """Integration tests for the custom base manager."""

  def test_get_zerotuplet(self) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    # Perform test.
    with self.assertRaises(ZeroTupletException):
      TestModel.objects.get()

  def test_get_twins(self) -> None :
    """Test if the correct exception gets thrown if two objects are found."""
    # Prepare data.
    TestModel().save()
    TestModel().save()
    # Perform test.
    with self.assertRaises(TwinException):
      TestModel.objects.get()

  def test_get(self) -> None :
    """Test if the correct exception gets thrown if no object is found."""
    # Prepare data.
    expected = TestModel()
    expected.save()
    # Perform test.
    result = TestModel.objects.get()
    # Assert result.
    self.assertEqual(expected, result)
