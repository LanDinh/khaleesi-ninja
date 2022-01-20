"""Base settings for backend services."""

# Python.
from os import environ
from typing import cast

# khaleesi.ninja.
from . import definition as definition  # pylint: disable=useless-import-alias


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


# khaleesi.ninja
KHALEESI_NINJA: definition.KhaleesiNinjaSettings = definition.KhaleesiNinjaSettings(
  METADATA = definition.Metadata(
    GATE    = environ['KHALEESI_GATE'],
    SERVICE = environ['KHALEESI_SERVICE'],
    TYPE    = definition.ServiceType.MICRO,
    VERSION = environ['KHALEESI_VERSION'],
  ),
  GRPC = definition.Grpc(
    PORT     = cast(int, environ.get('PORT', 8000)),
    HANDLERS = [],
    THREADS = cast(int, environ.get('THREADS', 10))
  ),
  MONITORING = definition.Monitoring(
    PORT = cast(int, environ.get('KHALEESI_METRICS_PORT', 8020)),
  ),
  CORE = definition.Core(
    STRUCTURED_LOGGING_METHOD = definition.StructuredLoggingMethod.GRPC,
  ),
)
