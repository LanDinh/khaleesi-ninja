"""Settings for core-sawmill."""

# pylint: disable=undefined-variable

# khaleesi-ninja.
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


KHALEESI_NINJA['GRPC']['INTERCEPTORS']['STRUCTURED_LOGGER']['NAME'] = \
  'microservice.structured_logger.StructuredDbLogger'
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.forester')
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.lumberjack')
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.sawyer')
KHALEESI_NINJA['STARTUP']['MIGRATIONS_BEFORE_SERVER_START']['REQUIRED']  = True
KHALEESI_NINJA['STARTUP']['MIGRATIONS_BEFORE_SERVER_START']['MIGRATION'] = '0001'


# Cache.
# noinspection SpellCheckingInspection
CACHES['service-registry'] = {
    'BACKEND' : 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'service-registry',
    'TIMEOUT' : 86400,  # type: ignore[dict-item]
}
