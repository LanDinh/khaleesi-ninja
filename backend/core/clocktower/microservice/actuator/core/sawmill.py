"""core-sawmill batch jobs."""

# Python.
from typing import cast

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.proto.core_pb2 import JobRequest, EmptyResponse
from khaleesi.proto.core_sawmill_pb2_grpc import SawyerStub


STUB = SawyerStub(CHANNEL_MANAGER.get_channel(gate = 'core', service = 'sawmill'))  # type: ignore[no-untyped-call]  # pylint: disable=line-too-long


def cleanup_events(request: JobRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupEvents(request))

def cleanup_grpc_requests(request: JobRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupGrpcRequests(request))

def cleanup_errors(request: JobRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupErrors(request))

def cleanup_http_requests(request: JobRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupHttpRequests(request))

def cleanup_queries(request: JobRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupQueries(request))


SAWMILL = {
    'cleanup-events'       : cleanup_events,
    'cleanup-grpc-requests': cleanup_grpc_requests,
    'cleanup-errors'       : cleanup_errors,
    'cleanup-http-requests': cleanup_http_requests,
    'cleanup-queries'      : cleanup_queries,
}
