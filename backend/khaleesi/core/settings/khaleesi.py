"""Base settings for backend services."""

# Python.
from os import environ
from typing import TypedDict, List, cast


# Base definition.
DEBUG = 'KHALEESI_DEBUG' in environ
TIME_ZONE = 'UTC'
USE_TZ = True


# Installed apps.
INSTALLED_APPS = [
  'khaleesi',  # custom commands.
]


# Database.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# khaleesi.ninja.
class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""
  PORT: int
  GRPC_HANDLERS: List[str]

KHALEESI_NINJA: KhaleesiNinjaSettings = KhaleesiNinjaSettings(
  PORT = cast(int, environ.get('PORT', 8000)),
  GRPC_HANDLERS = [],
)
