"""Settings for core-guard."""

# pylint: disable=undefined-variable

# khaleesi-ninja.
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


INSTALLED_APPS.append('microservice')
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service')
