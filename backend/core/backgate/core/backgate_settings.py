"""Base settings for backgates."""

# khaleesi-ninja.
from khaleesi.core.khaleesi_settings import  *  # pylint: disable=wildcard-import,unused-wildcard-import

KHALEESI_NINJA['GRPC_HANDLERS'].append('core.service')  # pylint: disable=undefined-variable,line-too-long
