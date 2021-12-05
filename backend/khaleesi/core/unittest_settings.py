"""Base settings for backend services."""

# Python.
from pathlib import Path

# khaleesi.ninja
from typing import Dict, Any

# noinspection PyUnresolvedReferences
from settings import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Base definition.
SECRET_KEY = 'development-keys-are-not-secret-change-before-production!'


# Database.
PROJECT_DIR = Path(__file__).resolve().parent.parent
TEST_DATABASE = {
  'ENGINE': 'django.db.backends.sqlite3',
  'NAME': PROJECT_DIR / 'db.sqlite3',
}
TEST_DATABASE_TEST_SETTINGS: Dict[str, Any] = {
  'DEPENDENCIES': []
}
DATABASES: Dict[str, Any] = {
  'default': {},
  'read': {
    **TEST_DATABASE,
    'TEST': {
      **TEST_DATABASE_TEST_SETTINGS,
      'MIRROR': 'write',
    },
  },
  'write': {
    **TEST_DATABASE,
    'TEST': TEST_DATABASE_TEST_SETTINGS,
  },
}
DATABASE_ROUTERS = [ 'khaleesi.core.unittest_database_router.TestDatabaseRouter' ]
