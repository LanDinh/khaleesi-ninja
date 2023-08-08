"""core_clocktower bellringer service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.proto.core_pb2 import ObjectMetadataRequest
from khaleesi.proto.core_clocktower_pb2 import DESCRIPTOR, JobRequest
from khaleesi.proto.core_clocktower_pb2_grpc import (
    BellRingerServicer as Servicer,
    add_BellRingerServicer_to_server as addToServer
)
from microservice.actuator.actuator import ACTUATOR
from microservice.models import Job


class Service(Servicer):
  """core_clocktower bellringer service."""

  def CreateJob(self, request: JobRequest, _: grpc.ServicerContext) -> JobRequest :
    """Create a new job."""
    LOGGER.info('Creating the new job.')
    job = Job.objects.khaleesiCreate(grpc = request.job)
    response = JobRequest()
    response.metadata.CopyFrom(job.toObjectMetadata())
    response.job.CopyFrom(job.toGrpc())
    return response

  def ExecuteJob(self, request: ObjectMetadataRequest, _: grpc.ServicerContext) -> ObjectMetadata :
    """Execute a job by ID."""
    LOGGER.info(f'Executing job "{request.object.id}".')
    job = Job.objects.get(khaleesiId = request.object.id)
    action, jobExecutionRequest = job.toGrpcJobExecutionRequest()
    return ACTUATOR.actuate(action = action, request = jobExecutionRequest)


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['BellRinger'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
