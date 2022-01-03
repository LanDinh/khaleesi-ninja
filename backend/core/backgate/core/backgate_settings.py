"""Base settings for backgates."""

# khaleesi-ninja.
from khaleesi.core.settings.definition import KhaleesiNinjaServiceType
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


KHALEESI_NINJA['METADATA']['TYPE'] = KhaleesiNinjaServiceType.BACKGATE

INSTALLED_APPS.append('core')  # pylint: disable=undefined-variable
KHALEESI_NINJA['GRPC']['HANDLERS'].append('core.service')  # pylint: disable=undefined-variable
