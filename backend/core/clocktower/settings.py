"""Settings for core_clocktower."""

# pylint: disable=undefined-variable

# khaleesi-ninja.
from khaleesi.core.settings.khaleesi import  *  # pylint: disable=wildcard-import,unused-wildcard-import
from khaleesi.core.settings.definition import GrpcEventMethodName


KHALEESI_NINJA['GRPC']['HANDLERS'].append('microservice.service.bellringer')
KHALEESI_NINJA['GRPC']['SERVER_METHOD_NAMES']['APP_SPECIFIC'] = {
    'UPDATE_JOB_EXECUTION_STATE': GrpcEventMethodName(
      METHOD = 'update-job-execution-state',
      TARGET = 'core.core.job.execution',
    )
}
