"""core_clocktower service."""

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.proto.core_pb2 import IdMessage
from khaleesi.proto.core_clocktower_pb2 import DESCRIPTOR, Job as GrpcJob
from khaleesi.proto.core_clocktower_pb2_grpc import (
    BellRingerServicer as Servicer,
    add_BellRingerServicer_to_server as add_to_server
)
from microservice.models import Job


class Service(Servicer):
  """core_clocktower service."""

  def CreateJob(self, request: GrpcJob, _: grpc.ServicerContext) -> IdMessage :
    """Create a new job."""
    LOGGER.info('Creating the new job.')
    job = Job.objects.create_job(grpc_job = request)
    response = IdMessage()
    response.id = job.job_id
    return response


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['BellRinger'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
