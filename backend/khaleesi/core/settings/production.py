"""Base settings for backend services."""

# Python.
# noinspection PyUnresolvedReferences
from os import environ

# khaleesi.ninja.
# noinspection PyUnresolvedReferences
from settings import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Base definition.
SECRET_KEY = environ['KHALEESI_SECRET_KEY']


# Database.
DATABASE = {
  'ENGINE' : 'django.db.backends.postgresql',
  'HOST'   : environ['KHALEESI_DATABASE_HOST'],
  'PORT'   : environ['KHALEESI_DATABASE_PORT'],
  'NAME'   : environ['KHALEESI_DATABASE_NAME'],
  'OPTIONS': {
    'options': '-c search_path=khaleesi'
  },
}
DATABASES = {
  'default': {
      **DATABASE,  # type: ignore[arg-type]
      'USER'    : environ['KHALEESI_DATABASE_USER'],
      'PASSWORD': environ['KHALEESI_DATABASE_PASSWORD'],
  },
  'migrate': {
    **DATABASE,  # type: ignore[arg-type]
    'USER'    : environ['KHALEESI_DATABASE_SUPERUSER'],
    'PASSWORD': environ['KHALEESI_DATABASE_SUPERUSER_PASSWORD'],
  },
}
