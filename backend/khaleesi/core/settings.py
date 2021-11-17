"""Base settings for backend services."""

# Python.
from os import environ
from pathlib import Path
from typing import TypedDict, List, cast


# Base definition.
SECRET_KEY = 'development-keys-are-not-secret-change-before-production!'
DEBUG = 'KHALEESI_DEBUG' in environ
TIME_ZONE = 'UTC'
USE_TZ = True


# Installed apps.
INSTALLED_APPS = [
  'khaleesi',  # custom commands.
  'core',  # common models.
]


# Database.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': PROJECT_DIR / 'db.sqlite3',
  }
}
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
