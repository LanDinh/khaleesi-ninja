"""Settings for core-sawmill."""

# pylint: disable=undefined-variable

# khaleesi-ninja.
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


INSTALLED_APPS.append('microservice')
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.lumberjack')
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.sawyer')

KHALEESI_NINJA['CORE']['STRUCTURED_LOGGING_METHOD'] = definition.StructuredLoggingMethod.DATABASE
