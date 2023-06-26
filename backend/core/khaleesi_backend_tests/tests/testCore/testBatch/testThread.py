"""Test the thread utility."""

# Python.
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.batch.thread import BatchJobThread
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionMetadata


class BatchJobThreadTestCase(SimpleTestCase):
  """Test the thread utility."""

  def testRun(self) -> None :
    """Test if running the thread works as expected."""
    # Prepare data.
    job = MagicMock()
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    # Execute test.
    thread.start()
    # Assert result.
    job.execute.assert_called_once_with(stopEvent = thread.stopEvent)

  def testStop(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    thread = BatchJobThread(job = MagicMock())  # type: ignore[var-annotated]
    # Execute test.
    thread.stop()
    # Assert result.
    self.assertTrue(thread.stopEvent.is_set())

  def testThreadStartsStopped(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    thread = BatchJobThread(job = MagicMock())  # type: ignore[var-annotated]
    # Execute test.
    result = thread.stopEvent.is_set()
    # Assert result.
    self.assertFalse(result)

  def testIsBatchJobThread(self) -> None :
    """Test if the thread type can be correctly identified."""
    # Prepare data.
    thread: BatchJobThread[MagicMock] = BatchJobThread(job = MagicMock())
    # Execute test.
    result = thread.isBatchJobThread
    # Assert result.
    self.assertTrue(result)

  def testIsJob(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    metadata             = JobExecutionMetadata()
    metadata.jobId       = 'job'
    metadata.executionId = 13
    job = MagicMock()
    job.job = metadata
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    # Execute test.
    result = thread.isJob(job = metadata)
    # Assert result.
    self.assertTrue(result)

  def testIsNotJob(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    job                 = MagicMock()
    job.job.jobId       = 'job'
    job.job.executionId = 13
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    for jobId, executionId in [ ('not-job', 13), ('job', 1337), ('not-job', 1337) ]:
      with self.subTest(job = jobId, execution = executionId):
        metadata             = JobExecutionMetadata()
        metadata.jobId       = jobId
        metadata.executionId = executionId
        # Execute test.
        result = thread.isJob(job = metadata)
        # Assert result.
        self.assertFalse(result)
