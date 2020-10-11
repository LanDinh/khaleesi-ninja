"""ASGI config for base project."""

# Python.
import os

# Django.
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuration.settings')
application = get_asgi_application()
