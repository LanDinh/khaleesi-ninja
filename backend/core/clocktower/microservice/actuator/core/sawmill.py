"""core-sawmill batch jobs."""

# Python.
from typing import cast

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.proto.core_pb2 import JobCleanupRequest, EmptyResponse
from khaleesi.proto.core_sawmill_pb2_grpc import SawyerStub


STUB = SawyerStub(CHANNEL_MANAGER.get_channel(gate = 'core', service = 'sawmill'))  # type: ignore[no-untyped-call]  # pylint: disable=line-too-long


def cleanup_requests(request: JobCleanupRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, STUB.CleanupRequests(request))


SAWMILL = {
    'cleanup-requests': cleanup_requests,
}
