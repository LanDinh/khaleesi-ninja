"""Test the custom base manager."""

# khaleesi.ninja.
from common.exceptions import ZeroTupletException, TwinException
from test_util.test import TestCase
from .models import TestModel, TestRelation


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

  def test__get_queryset_one_to_one(self) -> None :
    """Test if the _get_queryset method works as intended."""
    # Prepare data.
    model = TestModel()
    model.save()
    relation = TestRelation(one_to_one = model)
    relation.save()
    # Perform test.
    result_model = relation.one_to_one
    result_relation = model.one_to_one  # type: ignore[attr-defined]  # pylint: disable=no-member
    # Assert result.
    self.assertEqual(model.pk, result_model.pk)  # pylint: disable=no-member
    self.assertEqual(relation.pk, result_relation.pk)

  def test__get_queryset_one_to_many(self) -> None :
    """Test if the _get_queryset method works as intended."""
    # Prepare data.
    model = TestModel()
    model.save()
    relation1 = TestRelation(one_to_many = model)
    relation1.save()
    relation2 = TestRelation()
    relation2.save()
    # Perform test.
    result_model = relation1.one_to_many
    result_relation = model.one_to_many.get()  # type: ignore[attr-defined]  # pylint: disable=no-member
    # Assert result.
    self.assertEqual(model.pk, result_model.pk)  # pylint: disable=no-member
    self.assertEqual(relation1.pk, result_relation.pk)

  def test__get_queryset_many_to_many(self) -> None :
    """Test if the _get_queryset method works as intended."""
    # Prepare data.
    model1 = TestModel()
    model1.save()
    model2 = TestModel()
    model2.save()
    relation1 = TestRelation()
    relation1.save()
    relation2 = TestRelation()
    relation2.save()
    relation1.many_to_many.add(model1)  # pylint: disable=no-member
    # Perform test.
    result_model = relation1.many_to_many.get()  # pylint: disable=no-member
    result_relation = model1.many_to_many.get()   # type: ignore[attr-defined]  # pylint: disable=no-member
    # Assert result.
    self.assertEqual(model1.pk, result_model.pk)
    self.assertEqual(relation1.pk, result_relation.pk)
    with self.assertRaises(ZeroTupletException):
      relation2.many_to_many(manager = 'objects').get()  # pylint: disable=no-member,not-callable
    with self.assertRaises(ZeroTupletException):
      model2.many_to_many(manager = 'objects').get()   # type: ignore[attr-defined]  # pylint: disable=no-member
