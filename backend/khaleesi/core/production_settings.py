"""Base settings for backend services."""

# Python.
from os import environ

# khaleesi.ninja.
# noinspection PyUnresolvedReferences
from settings import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Base definition.
SECRET_KEY = environ['KHALEESI_SECRET_KEY']


# Database.
DATABASE_ROUTERS = [ 'khaleesi.core.database_router.DatabaseRouter' ]
