"""Base settings for backend services."""

# Python.
from os import environ
from pathlib import Path


# Base definition.
SECRET_KEY = 'test'
DEBUG = environ.get('KHALEESI_DEBUG', False)
TIME_ZONE = 'UTC'
USE_TZ = True


# Installed apps.
INSTALLED_APPS = [
    'khaleesi',  # custom commands.
    'core',      # common models.
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
