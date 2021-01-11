"""Custom base model to configure default managers."""

# Python.
from __future__ import annotations
from enum import EnumMeta, Enum
from typing import List, Tuple

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.manager import Manager


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
def choices(enum_type: EnumMeta) -> List[Tuple[Enum, str]] :
  """Get the choices list necessary for models."""
  return [(tag.name, tag.value) for tag in enum_type]  # type: ignore[var-annotated]


class Model(models.Model):
  """Custom base model to configure default managers."""

  _objects = models.Manager()
  objects: Manager[Model] = Manager()

  class Meta:
    """Define the default manager."""
    abstract = True
    default_manager_name = '_objects'
    base_manager_name = 'objects'
