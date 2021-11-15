"""Base settings for backend services."""

# Python.
from os import environ
from pathlib import Path


# Base definition.
SECRET_KEY = 'development-keys-are-not-secret-change-before-production!'
DEBUG = True if 'KHALEESI_DEBUG' in environ else False
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
KHALEESI_NINJA = {
  'PORT': environ.get('PORT', 8000),
}
