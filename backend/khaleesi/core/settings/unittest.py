"""Base settings for backend services."""

# Python.
from pathlib import Path
from typing import Dict, Any

# khaleesi.ninja
# noinspection PyUnresolvedReferences
from settings import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Base definition.
SECRET_KEY = 'development-keys-are-not-secret-change-before-production!'


# Database.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASES: Dict[str, Any] = {
  'default': {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME'  : PROJECT_DIR / 'db.sqlite3',
  },
}

# noinspection PyUnresolvedReferences
INSTALLED_APPS.append('tests')

# khaleesi.ninja.
# noinspection PyUnresolvedReferences
KHALEESI_NINJA['GRPC']['SHUTDOWN_GRACE_SECS'] = 1
