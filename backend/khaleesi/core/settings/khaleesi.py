"""Base settings for backend apps."""

# Python.
from os import environ
from typing import cast

# khaleesi.ninja.
from . import definition as definition  # pylint: disable=useless-import-alias


# Base definition.
DEBUG     = 'KHALEESI_DEBUG' in environ
TIME_ZONE = 'UTC'
USE_TZ    = True


# Installed apps.
# noinspection PyUnresolvedReferences
INSTALLED_APPS = [
  'khaleesi',  # custom commands.
  'microservice',  # code for microservices.
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
              '| {levelname: >8} | {asctime} | {thread:d} | {grpcRequestId: <36} | {message}',
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


# khaleesi.ninja.
KHALEESI_NINJA: definition.KhaleesiNinjaSettings = definition.KhaleesiNinjaSettings(
  METADATA = definition.Metadata(
    SITE    = environ['SITE'],
    APP     = environ['APP'],
    TYPE    = definition.AppType.MICRO,
    VERSION = environ['KHALEESI_VERSION'],
    POD_ID  = environ['HOSTNAME'],
  ),
  GRPC = definition.Grpc(
    PORT                = cast(int, environ.get('PORT', 8000)),
    THREADS             = cast(int, environ.get('THREADS', 10)),
    SHUTDOWN_GRACE_SECS = 30,
    SERVER_METHOD_NAMES = definition.GrpcServerMethodNames(
      SERVICE_NAME = 'grpc-server',
      USER_ID      = 'grpc-server',
      MIGRATE = definition.GrpcEventMethodName(
        METHOD = 'migrate',
        TARGET = 'core.core.server'
      ),
      INITIALIZE = definition.GrpcEventMethodName(
        METHOD = 'initialize',
        TARGET = 'core.core.server'
      ),
      LIFECYCLE = definition.GrpcEventMethodName(
        METHOD = 'lifecycle',
        TARGET = 'core.core.server'
      ),
      INITIALIZE_REQUEST_METRICS = definition.GrpcEventMethodName(
        METHOD = 'initialize-request-metrics',
        TARGET = 'core.core.metrics.request',
      ),
      APP_SPECIFIC = {},
    ),
    HANDLERS = [ 'khaleesi.core.service.maid' ],
  ),
  MONITORING = definition.Monitoring(
    PORT = cast(int, environ.get('KHALEESI_METRICS_PORT', 8020)),
  ),
  SINGLETONS = definition.Singletons(
    STRUCTURED_LOGGER = definition.Singleton(
      NAME = 'khaleesi.core.logging.structuredLogger.StructuredGrpcLogger',
    ),
    BROOM = definition.Singleton(
      NAME = 'khaleesi.core.batch.broom.Broom',
    ),
  ),
  STARTUP = definition.Startup(
    MIGRATIONS_BEFORE_SERVER_START = definition.MigrationsBeforeServerStart(
      REQUIRED  = False,
      MIGRATION = '',
    ),
  ),
  BATCH = definition.Batch(TARGET_TYPE = 'core.core.table'),
)
