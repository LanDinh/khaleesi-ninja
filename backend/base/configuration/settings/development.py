"""Development settings for khaleesi.ninja."""

# pylint: disable=wildcard-import,unused-wildcard-import

# khaleesi.ninja
from configuration.settings.base.development import *
from configuration.settings._base import *

INSTALLED_APPS = BASE_INSTALLED_APPS + KHALEESI_INSTALLED_APPS
