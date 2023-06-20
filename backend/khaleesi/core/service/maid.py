"""Maid service to clean up after batch jobs."""

# gRPC.
import grpc

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.service_configuration import ServiceConfiguration
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import (
  IdRequest,
  EmptyResponse,
  EmptyRequest,
  DESCRIPTOR,
)
from khaleesi.proto.core_pb2_grpc import (
  MaidServicer as Servicer,
  add_MaidServicer_to_server as add_to_server
)


class Service(Servicer):
  """Maid service to clean up after batch jobs."""

  def AbortBatchJob(self, request: IdRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Abort the specified job."""
    LOGGER.info(f'Aborting job with ID {request.idMessage.id}')
    JobExecution.objects.stop_job(id_message = request.idMessage)
    return EmptyResponse()

  def AbortAllBatchJobs(self, request: EmptyRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Abort all running batch jobs."""
    JobExecution.objects.stop_all_jobs()
    return EmptyResponse()


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Maid'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
