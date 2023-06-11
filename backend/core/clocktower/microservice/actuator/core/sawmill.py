"""core-sawmill batch jobs."""

# Python.
from typing import cast

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.proto.core_pb2 import JobCleanupRequest, EmptyResponse
from khaleesi.proto.core_sawmill_pb2_grpc import SawyerStub


STUB = SawyerStub(CHANNEL_MANAGER.get_channel(gate = 'core', service = 'sawmill'))  # type: ignore[no-untyped-call]  # pylint: disable=line-too-long


def cleanup_events(request: JobCleanupRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupEvents(request))

def cleanup_requests(request: JobCleanupRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupRequests(request))

def cleanup_errors(request: JobCleanupRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupErrors(request))

def cleanup_backgate_requests(request: JobCleanupRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupBackgateRequests(request))

def cleanup_queries(request: JobCleanupRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupQueries(request))


SAWMILL = {
    'cleanup-events'           : cleanup_events,
    'cleanup-requests'         : cleanup_requests,
    'cleanup-errors'           : cleanup_errors,
    'cleanup-backgate-requests': cleanup_backgate_requests,
    'cleanup-queries'          : cleanup_queries,
}
