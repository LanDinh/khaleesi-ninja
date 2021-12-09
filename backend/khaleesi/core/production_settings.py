"""Base settings for backend services."""

# Python.
from os import environ

# khaleesi.ninja.
# noinspection PyUnresolvedReferences
from settings import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Base definition.
SECRET_KEY = environ['KHALEESI_SECRET_KEY']


# Database.
DATABASE = {
  'ENGINE': 'django.db.backends.postgresql',
  'HOST': environ['KHALEESI_DATABASE_HOST'],
  'PORT': environ['KHALEESI_DATABASE_PORT'],
  'NAME': environ['KHALEESI_DATABASE_NAME'],
  'OPTIONS': {
    'options': '-c search_path=khaleesi'
  },
}
DATABASES = {
  'default': {},
  'read': {
    **DATABASE,
    'USER': environ['KHALEESI_DATABASE_READ_USER'],
    'PASSWORD': environ['KHALEESI_DATABASE_READ_PASSWORD'],
  },
  'write': {
    **DATABASE,
    'USER': environ['KHALEESI_DATABASE_WRITE_USER'],
    'PASSWORD': environ['KHALEESI_DATABASE_WRITE_PASSWORD'],
  },
  'migrate': {
    **DATABASE,
    'USER': environ['KHALEESI_DATABASE_SUPERUSER'],
    'PASSWORD': environ['KHALEESI_DATABASE_SUPERUSER_PASSWORD'],
  },
}
DATABASE_ROUTERS = [ 'khaleesi.core.database_router.DatabaseRouter' ]
