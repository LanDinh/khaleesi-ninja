"""core-sawmill batch jobs."""

# Python.
from typing import cast

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.proto.core_pb2 import JobExecutionRequest, EmptyResponse
from khaleesi.proto.core_sawmill_pb2_grpc import MaidStub


STUB = MaidStub(CHANNEL_MANAGER.getChannel(gate = 'core', service = 'sawmill'))  # type: ignore[no-untyped-call]  # pylint: disable=line-too-long


def cleanupEvents(request: JobExecutionRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupEvents(request))

def cleanupGrpcRequests(request: JobExecutionRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupGrpcRequests(request))

def cleanupErrors(request: JobExecutionRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupErrors(request))

def cleanupHttpRequests(request: JobExecutionRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupHttpRequests(request))

def cleanupQueries(request: JobExecutionRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupQueries(request))


SAWMILL = {
    'cleanup-events'       : cleanupEvents,
    'cleanup-grpc-requests': cleanupGrpcRequests,
    'cleanup-errors'       : cleanupErrors,
    'cleanup-http-requests': cleanupHttpRequests,
    'cleanup-queries'      : cleanupQueries,
}
