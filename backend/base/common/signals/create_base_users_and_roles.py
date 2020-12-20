"""Connect custom signals."""

# Python.
from typing import Any

# Django.
from django.apps.config import AppConfig as DjangoAppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# khaleesi.ninja.
from common.app_config import ServiceConfig
from common.models import User, Role


@receiver(post_migrate)
def create_base_users_and_roles(sender: DjangoAppConfig, **_: Any) -> None :
  """Create base users and roles."""
  if sender.name == 'common' and not isinstance(sender, ServiceConfig):
    User.migrations.create_superuser()
    User.migrations.create_anonymous_user()

  elif isinstance(sender, ServiceConfig):
    Role.migrations.create(service = sender.service)
    for role in sender.roles:
      Role.migrations.create(service = sender.service, name = role)
