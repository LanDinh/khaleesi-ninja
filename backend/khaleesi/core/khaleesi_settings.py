"""Base settings for backend services."""

# Python.
from os import environ
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
DATABASE = {
  'ENGINE': 'django.db.backends.postgresql',
  'HOST': 'core-kubegres',
  'PORT': '5432',
  'NAME': 'backgate',
}
DATABASES = {
  'default': {},
  'read': {
    **DATABASE,
    'USER': 'postgres',
    'PASSWORD': 'superUnsafeSecret',
  },
  'write': {
    **DATABASE,
    'USER': 'postgres',
    'PASSWORD': 'superUnsafeSecret',
  },
  'migrate': {
    **DATABASE,
    'USER': 'postgres',
    'PASSWORD': 'superUnsafeSecret',
  },
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATABASE_ROUTERS = [ 'khaleesi.core.database_router.DatabaseRouter' ]


# khaleesi.ninja.
class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""
  PORT: int
  GRPC_HANDLERS: List[str]

KHALEESI_NINJA: KhaleesiNinjaSettings = KhaleesiNinjaSettings(
  PORT = cast(int, environ.get('PORT', 8000)),
  GRPC_HANDLERS = [],
)
