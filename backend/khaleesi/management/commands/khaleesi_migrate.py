"""Command to start the gRPC server."""

# Python.
from typing import Any

# Django.
from django.conf import settings
from django.core.management.commands.migrate import Command as DjangoMigrateCommand

# khaleesi.ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.management.commands._base import BaseCommand


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Command(BaseCommand, DjangoMigrateCommand):
  """Command to migrate the gRPC server."""

  help = 'Applies migrations to the gRPC server.'

  def khaleesi_handle(self, *args: Any, **options: Any) -> None :
    """Apply migrations to the gRPC server."""
    DjangoMigrateCommand.handle(self, *args, **options)
