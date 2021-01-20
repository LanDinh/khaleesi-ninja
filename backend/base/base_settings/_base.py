"""The base configuration for khaleesi.ninja."""


# General settings.
DEBUG = False
ALLOWED_HOSTS = []


# Application definition
BASE_INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
    #'corsheaders',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',  # before session.
    'django.contrib.sessions.middleware.SessionMiddleware',
    # cors: before common.
    #'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # after authentication.
    # Custom middleware last.
    #'apps.common.user.middleware.KhaleesiUserMiddleware',
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

BASE_DATABASE = {
    'ENGINE': 'settings',
    'NAME': 'khaleesi_ninja',
}

# Database
DATABASES = {
    'default': {**BASE_DATABASE},
    'logging': {
        **BASE_DATABASE,
        'TEST': {
          'MIRROR': 'default',
        },
    },
}
DATABASE_ROUTERS = ['settings.database_router.LoggingRouter']
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'khaleesi.DEBUG',
        },
        'info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'khaleesi.INFO',
        },
        'warning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'khaleesi.WARNING',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'khaleesi.ERROR',
        },
        'django_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.INFO',
        },
        'django_warning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'django.WARNING',
        },
        'django_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'django.ERROR',
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['django_info', 'django_warning', 'django_error']
        },
        'khaleesi': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['debug', 'info', 'warning', 'error']
        },
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = []
AUTH_USER_MODEL = 'common.User'


# Internationalization
USE_I18N = False
USE_L10N = False
USE_TZ = True
TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'


# Cookies.
SESSION_COOKIE_DOMAIN="khaleesi.ninja"


# Django Rest Framework configuration.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['settings.permission.Permission'],
    'DEFAULT_RENDERER_CLASSES': ['settings.json.JSONRenderer'],
    'EXCEPTION_HANDLER': 'settings.exception_handler.exception_handler',
}

# khaleesi.ninja configuration.
KHALEESI_NINJA = {
    'BASE': {
        'USERS': {
            'ANONYMOUS': '',
            'SUPERUSER': 'khaleesi',
        },
        'MAX_FAILED_LOGIN_ATTEMPTS': 5,
    },
}
