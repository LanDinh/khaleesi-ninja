"""Test the custom base manager."""

# Python.
import inspect
from typing import Any, List, Tuple

# khaleesi.ninja.
from test_util.test import CombinedTestCase
from .models import TestModel


_IGNORE_MANAGER_METHODS = [
    'all',
    'check',
    'contribute_to_class',
    'db_manager',
    'deconstruct',
    'get_queryset',
    'from_queryset',
    'get',
    'using',
]

_IGNORE_QUERYSET_METHODS = ['all', 'get', 'using']


class ManagerTestCase(CombinedTestCase):
  """Test the custom base manager."""

  def test_queryset_copy(self) -> None :
    """Make sure that methods aren't exposed."""
    manager_methods = [name for (name, _) in self.get_manager_methods()]
    queryset_methods = [name for (name, _) in self.get_queryset_methods()]
    for queryset_method in queryset_methods:
      with self.subTest(queryset_method = queryset_method):
        self.assertFalse(queryset_method in manager_methods)

  def test_public_methods(self) -> None :
    """Don't expose the queryset."""
    for name, method in self.get_manager_methods():
      with self.subTest(method = name):
        with self.assertRaises(NotImplementedError):
          method()

  def get_manager_methods(self) -> List[Tuple[str, Any]] :
    """Return all public methods of the custom manager that have been manually erased."""
    return self._get_public_methods(obj = TestModel.objects, filtered = _IGNORE_MANAGER_METHODS)

  def get_queryset_methods(self) -> List[Tuple[str, Any]] :
    """Return all public methods of the queryset that have not been manually permitted."""
    return self._get_public_methods(
        obj = TestModel.objects.get_queryset(),
        filtered = _IGNORE_QUERYSET_METHODS,
    )

  @staticmethod
  def _get_public_methods(*, obj: Any, filtered: List[str]) -> List[Tuple[str, Any]] :
    """Return all public methods of the given object except those filtered."""
    return [
        (name, method) for name, method in inspect.getmembers(obj, predicate = inspect.ismethod)
        if not name.startswith('_') and not name in filtered
    ]
