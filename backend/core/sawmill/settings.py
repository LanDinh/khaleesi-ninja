"""Settings for core-sawmill."""

# pylint: disable=undefined-variable

# khaleesi-ninja.
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


INSTALLED_APPS.append('microservice')
KHALEESI_NINJA['GRPC']['INTERCEPTORS']['LOGGING_SERVER_INTERCEPTOR']['STRUCTURED_LOGGER'] = \
  'microservice.structured_logger.StructuredDbLogger'
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.forester')
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.lumberjack')
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.sawyer')



# Cache.
# noinspection SpellCheckingInspection
CACHES['service-registry'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'service-registry',
    'TIMEOUT': 86400,  # type: ignore[dict-item]
}
