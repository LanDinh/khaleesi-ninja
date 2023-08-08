"""Maid service to clean up after batch jobs."""

# gRPC.
import grpc

# khaleesi.ninja.
from khaleesi.core.batch.thread import stopAllJobs, stopJob
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.serviceConfiguration import ServiceConfiguration
from khaleesi.models.jobExecution import JobExecution
from khaleesi.proto.core_pb2 import (
  ObjectMetadataRequest,
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

  def AbortBatchJob(
      self,
      request: ObjectMetadataRequest,
      _      : grpc.ServicerContext,
  ) -> EmptyResponse :
    """Abort the specified job."""
    LOGGER.info(f'Aborting job with ID {request.object.id}')
    stopJob(jobs = JobExecution.objects.getJobExecutionsInProgress(job = request.object))
    return EmptyResponse()

  def AbortAllBatchJobs(self, request: EmptyRequest, _: grpc.ServicerContext) -> EmptyResponse :
    """Abort all running batch jobs."""
    LOGGER.info('Aborting all jobs.')
    stopAllJobs()
    return EmptyResponse()


serviceConfiguration = ServiceConfiguration[Service](
  name               = DESCRIPTOR.services_by_name['Maid'].full_name,
  addServiceToServer = addToServer,
  service            = Service()
)
