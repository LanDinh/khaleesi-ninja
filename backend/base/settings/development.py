"""Development settings for khaleesi.ninja."""

# pylint: disable=wildcard-import,unused-wildcard-import

# khaleesi.ninja
from settings._base import *


# Debug settings.
SECRET_KEY = 'r@q)h2se75d-_c&c#uzuupvf#u9-(@%@vhulk5#7&!be0f(vur'
DEBUG = True
ALLOWED_HOSTS.append('base.api.khaleesi.ninja')


# Database settings.
DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = ''
DATABASES['default']['USER'] = 'khaleesi_ninja'
DATABASES['default']['PASSWORD'] = ''


# Rest settings.
#REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
#    'rest_framework.renderers.BrowsableAPIRenderer',
#)


# CORS & cross-site configuration.
#CORS_ORIGIN_WHITELIST = [
#    'http://127.0.0.1:3000',
#]
#CORS_ALLOW_CREDENTIALS = True
#SESSION_COOKIE_SAMESITE = None
#CSRF_COOKIE_SAMESITE = None
#CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:3000']
