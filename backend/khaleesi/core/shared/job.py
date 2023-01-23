"""Job utility"""

# Python.
from functools import wraps
from typing import Callable, Tuple, TypeVar

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse, JobCleanupRequest


T = TypeVar('T')


def job() -> Callable[
  [Callable[[T, JobCleanupRequest], Tuple['JobExecutionResponse.Status.V', int, str]]],
  Callable[[T, JobCleanupRequest], JobExecutionResponse],
] :
  """Execute a method as job, by entering intermediary entries into a local table."""

  def decorator(
      func: Callable[[T, JobCleanupRequest], Tuple['JobExecutionResponse.Status.V', int, str]],
  ) -> Callable[[T, JobCleanupRequest], JobExecutionResponse] :

    @wraps(func)
    def wrapped(self: T, request: JobCleanupRequest) -> JobExecutionResponse :
      job_execution = JobExecution.objects.start_job_execution(job = request.job)
      if job_execution.in_progress:
        try:
          LOGGER.info('Executing the job.')
          status, items_processed, details = func(self, request)
          job_execution.finish(
            status          = status,
            items_processed = items_processed,
            details         = details,
          )
        except Exception:  # pylint: disable=broad-except
          job_execution.finish(
            status          = JobExecutionResponse.Status.ERROR,
            items_processed = -1,
            details         = 'Exception happened during job execution.',
          )
      else:
        LOGGER.warning('Skipping job execution!')
      return job_execution.to_grpc_job_execution_response()

    return wrapped

  return decorator
