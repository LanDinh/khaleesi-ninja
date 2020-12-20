"""Custom AppConfig."""

# Python.
from abc import ABC, abstractmethod
from typing import List

# Django.
from django.apps import AppConfig as DjangoAppConfig

# khaleesi.ninja.
from common.service_type import ServiceType


class ServiceConfig(DjangoAppConfig, ABC):
  """Custom AppConfig."""

  @property
  @abstractmethod
  def service(self) -> ServiceType :
    """Force setting of the name."""

  @property
  @abstractmethod
  def roles(self) -> List[str] :
    """Force setting a list of roles."""
