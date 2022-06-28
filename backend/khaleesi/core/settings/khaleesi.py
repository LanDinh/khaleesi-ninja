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


# Logging.
# noinspection SpellCheckingInspection
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'khaleesi': {
            'format':
              '| {levelname} | {asctime} | {thread:d} | {request_id} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'khaleesi_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'khaleesi',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'khaleesi': {
            'handlers': ['khaleesi_console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}


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
