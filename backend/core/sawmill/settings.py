"""Settings for core-sawmill."""

# khaleesi-ninja.
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


INSTALLED_APPS.append('microservice')  # pylint: disable=undefined-variable
KHALEESI_NINJA['GRPC_HANDLERS'].append('microservice.service')  # pylint: disable=undefined-variable
