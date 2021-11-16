"""Base settings for backgates."""

# khaleesi-ninja.
from khaleesi.core.settings import *

KHALEESI_NINJA['GRPC_HANDLERS'].append('core.service')
