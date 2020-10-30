"""Turn test packages into apps to enable test-only models."""

# Python.
from typing import Any

# Django.
from django.apps import AppConfig, apps


def setup_test_app(package: Any, label: str) -> None :
  """
  Setup a Django test app for the provided package to allow test models
  tables to be created if the containing app has migrations.

  This function should be called from app.tests __init__ module and pass
  along __package__.

  Source: https://code.djangoproject.com/ticket/7835#comment:46
  """
  app_config = AppConfig.create(package)
  app_config.apps = apps
  if label in apps.app_configs:
    return
  app_config.label = label
  apps.app_configs[app_config.label] = app_config
  app_config.import_models()
