"""Base settings for backgates."""

# khaleesi-ninja.
from khaleesi.core.settings.definition import ServiceType
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


KHALEESI_NINJA['METADATA']['TYPE'] = ServiceType.BACKGATE

INSTALLED_APPS.append('core')  # pylint: disable=undefined-variable
KHALEESI_NINJA['GRPC']['HANDLERS'].append('core.service')  # pylint: disable=undefined-variable
