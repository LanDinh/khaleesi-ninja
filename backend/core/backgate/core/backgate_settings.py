"""Base settings for backgates."""

# khaleesi-ninja.
from khaleesi.core.khaleesi_settings import  *  # pylint: disable=wildcard-import,unused-wildcard-import

INSTALLED_APPS.append('core')  # pylint: disable=undefined-variable
KHALEESI_NINJA['GRPC_HANDLERS'].append('core.service')  # pylint: disable=undefined-variable
