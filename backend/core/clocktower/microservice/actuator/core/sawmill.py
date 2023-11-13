"""core-sawmill batch jobs."""

# Python.
from typing import cast

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.proto.core_pb2 import JobExecutionRequest, EmptyResponse
from khaleesi.proto.core_pb2_grpc import MaidStub


CLEANUP_STUB = MaidStub(CHANNEL_MANAGER.getChannel(site = 'core', app = 'sawmill'))  # type: ignore[no-untyped-call]  # pylint: disable=line-too-long


def cleanup(request: JobExecutionRequest) -> EmptyResponse :
  """Cleanup requests."""
  return cast(EmptyResponse, CLEANUP_STUB.Cleanup(request))


SAWMILL = {
    'cleanup-events'       : cleanup,
    'cleanup-grpc-requests': cleanup,
    'cleanup-errors'       : cleanup,
    'cleanup-http-requests': cleanup,
    'cleanup-queries'      : cleanup,
}
