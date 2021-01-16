"""The different kinds of SQL operations."""

# pylint: disable=invalid-name

# Python.
from enum import Enum


class Operation(Enum):
  """The different kinds of languages."""
  SELECT = 'select'
  INSERT = 'insert'
  UPDATE = 'update'
  DELETE = 'delete'
