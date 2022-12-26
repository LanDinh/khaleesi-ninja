"""Settings for core-backgate."""

# khaleesi-ninja.
from khaleesi.core.settings.definition import ServiceType
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import


KHALEESI_NINJA['METADATA']['TYPE'] = ServiceType.BACKGATE
KHALEESI_NINJA['GRPC']['INTERCEPTORS']['REQUEST_STATE']['NAME'] = \
  'microservice.request_state_interceptor.BackgateRequestStateServerInterceptor'
KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.service')
