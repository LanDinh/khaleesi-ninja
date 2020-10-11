"""The base configuration for khaleesi.ninja."""

# Python.
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# General settings.
DEBUG = False
ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    # django.
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',  # before session.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # after authentication.
]
ROOT_URLCONF = 'configuration.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'configuration.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'khaleesi_ninja',
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = []


# Internationalization
USE_I18N = False
USE_L10N = False
USE_TZ = False


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'


# Cookies.
SESSION_COOKIE_DOMAIN="khaleesi.ninja"


# Django Rest Framework configuration.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
}
