"""Custom model managers to restrict access."""

# pylint: disable=protected-access,line-too-long

# Python.
from typing import Any, Dict, TypeVar, Callable

# Django.
from django.db import models
from django.db.models import QuerySet
from django.db.models.manager import BaseManager as DjangoBaseManager

# khaleesi.ninja.
from common.exceptions import TwinException, ZeroTupletException


_METHODS_FOR_COPYING = ['using', '_insert']

T = TypeVar("T", bound = models.Model, covariant=True)  # pylint: disable=invalid-name


# noinspection PyUnresolvedReferences,PyTypeHints,SyntaxError,PyTypeChecker,PyMissingOrEmptyDocstring
class BaseManager(DjangoBaseManager):  # type: ignore[type-arg]
  """Custom base manager to restrict access."""

  @classmethod
  def _get_queryset_methods(cls, queryset_class: type) -> Dict[str, Any] :
    """Only override the things I want."""

    def create_method(*, name: str, method: Callable) -> Callable :  # type: ignore[type-arg]
      """Create a method passing on to the queryset."""
      def manager_method(self: Any, *args: Any, **kwargs: Any) -> Any:
        """Pass on from the queryset."""
        return getattr(self.get_queryset(), name)(*args, **kwargs)
      manager_method.__name__ = method.__name__
      manager_method.__doc__ = method.__doc__
      return manager_method

    # noinspection PyProtectedMember
    new_methods = super()._get_queryset_methods(queryset_class = queryset_class)
    return {
        name: create_method(name = name, method = method)
        for (name, method) in new_methods.items()
        if name in _METHODS_FOR_COPYING
    }

  def get(self, **kwargs: Any) -> T :  # type: ignore[override]
    """Get a single element."""
    result: QuerySet[T] = self.get_queryset().filter(**kwargs)
    if len(result) > 1:
      raise TwinException()
    if len(result) < 1:
      raise ZeroTupletException()
    return result[0]


# noinspection PyUnresolvedReferences,PyClassHasNoInit,PyMissingOrEmptyDocstring
class Manager(BaseManager.from_queryset(QuerySet)):  # type: ignore[misc]
  """Custom manager to restrict access."""
