"""Development settings for khaleesi.ninja."""

# pylint: disable=wildcard-import,unused-wildcard-import

# khaleesi.ninja
from configuration.settings._base import *
from base_settings.development import *

INSTALLED_APPS = BASE_INSTALLED_APPS + KHALEESI_INSTALLED_APPS
