"""Connect custom signals."""

# Python.
from typing import Any

# Django.
from django.apps.config import AppConfig as DjangoAppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# khaleesi.ninja.
from common.app_config import AppConfig
from common.models import Group, User
from settings.settings import Settings


@receiver(post_migrate)
def create_base_groups_and_users(sender: DjangoAppConfig, **_: Any) -> None :
  """Create custom groups and permissions."""
  if isinstance(sender, AppConfig) and sender.service_name == 'base':
    User.migrations.create_superuser()
    User.migrations.create_anonymous_user()
    Group.migrations.create(name = Settings.dragon_groupname())
    Group.migrations.create(name = Settings.warg_groupname())
    Group.migrations.create(name = Settings.missandei_groupname())
