"""Test the thread utility."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.batch.thread import BatchJobThread, stopJob, stopAllJobs
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata



class StopBatchJobsTestCase(SimpleTestCase):
  """Test if stopping batch jobs works."""

  @patch('khaleesi.core.batch.thread.threadingEnumerate')
  def testStopBatchJob(self, threads: MagicMock, *_: MagicMock) -> None :
    """Test aborting a specific job."""
    # Prepare data.
    threadToStop = MagicMock()
    threadToStop.isBatchJobThread  = True
    threadToStop.isJob.side_effect = [ True, False ]
    threadToNotStop = MagicMock([ 'stop' ])
    threads.return_value = [ threadToStop, threadToNotStop ]
    # Execute test.
    stopJob(jobs = [ MagicMock(), MagicMock() ])
    # Assert result.
    threadToStop.stop.assert_called_once()
    threadToNotStop.stop.assert_not_called()

  @patch('khaleesi.core.batch.thread.threadingEnumerate')
  def testStopAllBatchJobs(self, threads: MagicMock, *_: MagicMock) -> None :
    """Test aborting a specific job."""
    # Prepare data.
    threadToStop = MagicMock()
    threadToStop.isBatchJobThread = True
    threadToNotStop = MagicMock([ 'stop' ])
    threads.return_value = [ threadToStop, threadToNotStop ]
    # Execute test.
    stopAllJobs()
    # Assert result.
    threadToStop.stop.assert_called_once()
    threadToNotStop.stop.assert_not_called()

class BatchJobThreadTestCase(SimpleTestCase):
  """Test the thread utility."""

  @patch('khaleesi.core.shared.state.STATE')
  def testRun(self, state: MagicMock) -> None :
    """Test if running the thread works as expected."""
    # Prepare data.
    job = MagicMock()
    thread = BatchJobThread(job = job, stateRequest = MagicMock(), stateQueries = [])  # type: ignore[var-annotated]  # pylint: disable=line-too-long
    # Execute test.
    thread.start()
    # Assert result.
    job.execute.assert_called_once_with(stopEvent = thread.stopEvent)
    state.copyFrom.assert_called_once()

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
    """Test if the job can be identified."""
    # Prepare data.
    metadata    = ObjectMetadata()
    metadata.id = 'job'
    job = MagicMock()
    job.request.jobMetadata = metadata
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    # Execute test.
    result = thread.isJob(job = metadata)
    # Assert result.
    self.assertTrue(result)

  def testIsNotJob(self) -> None :
    """Test if the job can be identified."""
    # Prepare data.
    job = MagicMock()
    job.request.jobMetadata.id = 'job'
    thread = BatchJobThread(job = job)  # type: ignore[var-annotated]
    metadata    = ObjectMetadata()
    metadata.id = 'not-job'
    # Execute test.
    result = thread.isJob(job = metadata)
    # Assert result.
    self.assertFalse(result)
