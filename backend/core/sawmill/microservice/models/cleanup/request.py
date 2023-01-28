"""Request logs."""

# Python.
from __future__ import annotations

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.job import Job


class RequestCleanupJob(Job):
  """Clean up requests."""

  def execute_batch(self) -> int :
    """Execute one batch of the job and return the number of items that were processed."""
    LOGGER.info('Running batch.')
    return 1

  def count_total(self) -> int :
    """Count the total number of items that should be executed."""
    LOGGER.info('Counting batch.')
    return 5

  def target(self) -> str :
    """Return the target resource. By default, this is should be the affected model name."""
    return 'Request'
