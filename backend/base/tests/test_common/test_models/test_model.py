"""Test the custom base model."""

# pylint: disable=protected-access,line-too-long

# Django.
from django.apps import apps
from django.db import models

# khaleesi.ninja.
from common.models import Manager
from common.app_config import ServiceConfig
from test_util.test import CombinedTestCase


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class ModelTestCase(CombinedTestCase):
  """Test the custom base model."""

  def test_models(self) -> None :
    """Test if all custom models inherit from the custom base model."""
    for app in apps.app_configs.values():
      if isinstance(app, ServiceConfig):
        for name, model in app.models.items():
          if '_' not in name:  # Don't check related models.
            with self.subTest(model = name):
              # Check if the original manager is correctly registered.
              self.assertTrue(isinstance(model._objects, models.Manager))  # type: ignore[attr-defined]
              self.assertEqual('_objects', model._meta.default_manager_name)
              self.assertTrue(isinstance(model._meta.default_manager, models.Manager))
              # Check if the default manager is a custom one.
              self.assertTrue(issubclass(type(model.objects), Manager))
