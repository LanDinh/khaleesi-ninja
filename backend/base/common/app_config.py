"""Custom AppConfig."""

# Python.
from abc import ABC, abstractmethod

# Django.
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig, ABC):
  """Custom AppConfig."""

  @property
  @abstractmethod
  def service_name(self) -> str :
    """Force setting of the name."""
