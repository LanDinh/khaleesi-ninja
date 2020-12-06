"""Custom AppConfig."""

# Python.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

# Django.
from django.apps import AppConfig as DjangoAppConfig


@dataclass
class GroupMeta:
  """Attributes for the custom Group model."""
  name: str
  permissions: List[str]


@dataclass
class KhaleesiMeta:
  """Contains meta information of that model specific to this website."""
  # Automatically added to the anonymous user. Name: label.anonymous.
  anonymous_group_permissions: List[str] = field(default_factory = lambda: [])
  # Automatically added to all authenticated users. Name: label.authenticated.
  authenticated_group_permissions: List[str] =  field(default_factory = lambda: [])
  # All remaining groups. Should have a dragon baby as administrator.
  groups: List[GroupMeta] =  field(default_factory = lambda: [])


class AppConfig(DjangoAppConfig, ABC):
  """Custom AppConfig."""

  # noinspection SyntaxError,PyTypeHints
  @property
  @abstractmethod
  def name(self) -> str :  # type: ignore[override]
    """Force setting of the name."""

  @property
  @abstractmethod
  def khaleesi_meta(self) -> KhaleesiMeta :
    """Force setting of the meta info."""
