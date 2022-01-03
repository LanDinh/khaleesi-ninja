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
class KhaleesiNinjaGrpc(TypedDict):
  """Grpc configuration for khaleesi.ninja services."""

  PORT        : int
  HANDLERS    : List[str]

class KhaleesiNinjaMonitoring(TypedDict):
  """Grpc configuration for khaleesi.ninja services."""

  PORT        : int

class KhaleesiNinjaSettings(TypedDict):
  """Custom khaleesi.ninja settings."""

  GRPC      : KhaleesiNinjaGrpc
  MONITORING: KhaleesiNinjaMonitoring

KHALEESI_NINJA: KhaleesiNinjaSettings = KhaleesiNinjaSettings(
  GRPC = KhaleesiNinjaGrpc(
    PORT         = cast(int, environ.get('PORT', 8000)),
    HANDLERS     = [],
  ),
  MONITORING = KhaleesiNinjaMonitoring(
    PORT = cast(int, environ.get('KHALEESI_METRICS_PORT', 8020)),
  ),
)
