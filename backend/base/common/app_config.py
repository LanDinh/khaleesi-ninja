"""Custom AppConfig."""

# Python.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

# Django.
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig, ABC):
  """Custom AppConfig."""

  # noinspection SyntaxError,PyTypeHints
  @property
  @abstractmethod
  def service_name(self) -> str :  # type: ignore[override]
    """Force setting of the name."""
