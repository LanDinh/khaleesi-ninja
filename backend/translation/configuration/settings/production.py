"""Production settings for khaleesi.ninja."""

# pylint: disable=unused-wildcard-import

# khaleesi.ninja
from base.settings.production import *
from configuration.settings._base import *

INSTALLED_APPS = BASE_INSTALLED_APPS + KHALEESI_INSTALLED_APPS
