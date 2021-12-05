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
  'NAME': 'backgate',
  'HOST': environ['KHALEESI_DATABASE_HOST'],
  'PORT': environ['KHALEESI_DATABASE_PORT'],
}
DATABASES = {
  'default': {},
  'read': {
    **DATABASE,
    'PASSWORD': 'superUnsafeSecret',
    'USER': environ['KHALEESI_DATABASE_SUPERUSER'],
  },
  'write': {
    **DATABASE,
    'PASSWORD': 'superUnsafeSecret',
    'USER': environ['KHALEESI_DATABASE_SUPERUSER'],
  },
  'migrate': {
    **DATABASE,
    'PASSWORD': 'superUnsafeSecret',
    'USER': environ['KHALEESI_DATABASE_SUPERUSER'],
  },
}
DATABASE_ROUTERS = [ 'khaleesi.core.database_router.DatabaseRouter' ]
