"""Settings for core_clocktower."""

# pylint: disable=undefined-variable

# khaleesi-ninja.
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.bellringer')
