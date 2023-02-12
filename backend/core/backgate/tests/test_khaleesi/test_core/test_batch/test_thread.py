"""Test the thread utility."""

# Python.
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.batch.thread import BatchJobThread
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionMetadata


class BatchJobThreadTestCase(SimpleTestCase):
  """Test the thread utility."""

  def test_run(self) -> None :
    """Test if running the thread works as expected."""
    # Prepare data.
    job = MagicMock()
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    # Execute test.
    thread.start()
    # Assert result.
    job.execute.assert_called_once()

  def test_stop(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    thread = BatchJobThread(job = MagicMock())  # type: ignore[var-annotated]
    # Execute test.
    thread.stop()
    # Assert result.
    self.assertTrue(thread.is_stopped)

  def test_thread_starts_stopped(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    thread = BatchJobThread(job = MagicMock())  # type: ignore[var-annotated]
    # Execute test.
    result = thread.is_stopped
    # Assert result.
    self.assertFalse(result)

  def test_is_job(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    metadata = JobExecutionMetadata()
    metadata.job_id = 'job'
    metadata.execution_id = 13
    job = MagicMock()
    job.job = metadata
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    # Execute test.
    result = thread.is_job(job = metadata)
    # Assert result.
    self.assertTrue(result)

  def test_is_not_job(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    job = MagicMock()
    job.job.job_id = 'job'
    job.job.execution_id = 13
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    for job_id, execution_id in [ ('not-job', 13), ('job', 1337), ('not-job', 1337) ]:
      with self.subTest(job = job_id, execution = execution_id):
        metadata = JobExecutionMetadata()
        metadata.job_id = job_id
        metadata.execution_id = execution_id
        # Execute test.
        result = thread.is_job(job = metadata)
        # Assert result.
        self.assertFalse(result)
