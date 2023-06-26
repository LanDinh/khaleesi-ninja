"""Maid service to clean up after batch jobs."""

# gRPC.
import grpc

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import (
  IdRequest,
  EmptyResponse,
  EmptyRequest,
  DESCRIPTOR,
)
from khaleesi.proto.core_pb2_grpc import (
  MaidServicer as Servicer,
  add_MaidServicer_to_server as addToServer
)


class Service(Servicer):
  """Maid service to clean up after batch jobs."""

  def AbortBatchJob(self, request: IdRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Abort the specified job."""
    LOGGER.info(f'Aborting job with ID {request.idMessage.id}')
    JobExecution.objects.stopJob(idMessage = request.idMessage)
    return EmptyResponse()

  def AbortAllBatchJobs(self, request: EmptyRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Abort all running batch jobs."""
    JobExecution.objects.stopAllJobs()
    return EmptyResponse()


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Maid'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
