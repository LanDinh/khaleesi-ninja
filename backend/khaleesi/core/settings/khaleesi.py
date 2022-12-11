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
# No default cache, always explicitly name the caches!
CACHES = { 'default': { 'BACKEND': 'django.core.cache.backends.dummy.DummyCache' } }


# Logging.
# noinspection SpellCheckingInspection
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'khaleesi': {
            'format':
              '| {levelname: >8} | {asctime} | {thread:d} | {request_id: <36} | {message}',
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
    THREADS  = cast(int, environ.get('THREADS', 10)),
    SERVER_METHOD_NAMES = definition.GrpcServerMethodNames(
      SERVICE_NAME = 'grpc-server',
      USER_ID      = 'grpc-server',
      LIFECYCLE = definition.GrpcEventMethodNames(
        METHOD = 'lifecycle',
        TARGET = 'core.core.server'
      ),
      INITIALIZE_REQUEST_METRICS = definition.GrpcEventMethodNames(
        METHOD = 'initialize-request-metrics',
        TARGET = '',
      ),
    ),
    INTERCEPTORS = definition.GrpcInterceptors(
      LOGGING_SERVER_INTERCEPTOR = definition.GrpcLoggingServerInterceptor(
        STRUCTURED_LOGGER = 'khaleesi.core.shared.structured_logger.StructuredGrpcLogger',
      ),
    ),
    HANDLERS = [],
  ),
  MONITORING = definition.Monitoring(
    PORT = cast(int, environ.get('KHALEESI_METRICS_PORT', 8020)),
  ),
)
