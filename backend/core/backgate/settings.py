"""Settings for core-backgate."""

# khaleesi-ninja.
from core.backgate_settings import *  # pylint: disable=wildcard-import,unused-wildcard-import


KHALEESI_NINJA['GRPC']['INTERCEPTORS']['REQUEST_STATE']['NAME'] = \
  'microservice.request_state_interceptor.BackgateRequestStateServerInterceptor'
