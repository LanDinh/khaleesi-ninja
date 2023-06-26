"""core_clocktower service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.proto.core_pb2 import IdRequest, IdMessage, EmptyResponse
from khaleesi.proto.core_clocktower_pb2 import DESCRIPTOR, JobRequest
from khaleesi.proto.core_clocktower_pb2_grpc import (
    BellRingerServicer as Servicer,
    add_BellRingerServicer_to_server as addToServer
)
from microservice.actuator.actuator import ACTUATOR
from microservice.models import Job


class Service(Servicer):
  """core_clocktower service."""

  def CreateJob(self, request: JobRequest, _: grpc.ServicerContext) -> IdMessage :
    """Create a new job."""
    LOGGER.info('Creating the new job.')
    job = Job.objects.createJob(grpcJob = request.job)
    response = IdMessage()
    response.id = job.jobId
    return response

  def ExecuteJob(self, request: IdRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Execute a job by ID."""
    LOGGER.info(f'Executing job "{request.idMessage.id}".')
    action, jobRequest = Job.objects.getJobRequest(idMessage = request.idMessage)
    ACTUATOR.actuate(
      actionName = action,
      job        = jobRequest.job,
      action     = jobRequest.actionConfiguration,
      cleanup    = jobRequest.cleanupConfiguration,
    )
    return EmptyResponse()


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['BellRinger'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
