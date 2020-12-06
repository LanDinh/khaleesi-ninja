"""Add some custom properties to APIViews."""

# Python.
from abc import ABC, abstractmethod

# Django.
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView


class View(APIView, ABC):
  """Add custom attributes to APIViews."""

  @property
  @abstractmethod
  def permission(self) -> str :
    """Set the single permission determining access to this view."""


class GenericView(View, GenericAPIView, ABC):
  """Add custom attributes to GenericAPIViews."""
