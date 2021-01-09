"""Add some custom properties to APIViews."""

# Python.
from abc import ABC, abstractmethod

# Django.
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

# khaleesi.ninja.
from common.service_type import ServiceType


class View(APIView, ABC):
  """Add custom attributes to APIViews."""

  @property
  @abstractmethod
  def service(self) -> ServiceType :
    """Set the service this view belongs to."""

  @property
  @abstractmethod
  def feature(self) -> str :
    """Set the feature this view belongs to."""


class GenericView(View, GenericAPIView, ABC):
  """Add custom attributes to GenericAPIViews."""
