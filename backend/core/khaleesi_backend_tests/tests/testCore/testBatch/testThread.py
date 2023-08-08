"""Test the thread utility."""

# Python.
import sys
from unittest.mock import MagicMock, patch

# Django.
from django.test import tag

# khaleesi.ninja.
from khaleesi.core.batch.thread import BatchJobThread, stopJob, stopAllJobs
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata, RequestMetadata



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

  @tag('isolation')
  def testRun(self) -> None :
    """Test if running the thread works as expected."""
    with patch.dict(sys.modules, {'khaleesi.core.shared.state': MagicMock()}) as importDict:
      # Prepare data.
      job = MagicMock()
      thread: BatchJobThread[MagicMock] = BatchJobThread(
        job          = job,
        stateRequest = RequestMetadata(),
        stateQueries = [],
      )
      # Execute test.
      thread.start()
      # Assert result.
      importDict['khaleesi.core.shared.state'].STATE.copyFrom.assert_called_once()
      job.execute.assert_called_once_with(stopEvent = thread.stopEvent)

  def testStop(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    thread: BatchJobThread[MagicMock] = BatchJobThread(
      job          = MagicMock(),
      stateRequest = RequestMetadata(),
      stateQueries = [],
    )
    # Execute test.
    thread.stop()
    # Assert result.
    self.assertTrue(thread.stopEvent.is_set())

  def testThreadStartsStopped(self) -> None :
    """Test if stopping the thread works as expected."""
    # Prepare data.
    thread: BatchJobThread[MagicMock] = BatchJobThread(
      job          = MagicMock(),
      stateRequest = RequestMetadata(),
      stateQueries = [],
    )
    # Execute test.
    result = thread.stopEvent.is_set()
    # Assert result.
    self.assertFalse(result)

  def testIsBatchJobThread(self) -> None :
    """Test if the thread type can be correctly identified."""
    # Prepare data.
    thread: BatchJobThread[MagicMock] = BatchJobThread(
      job          = MagicMock(),
      stateRequest = RequestMetadata(),
      stateQueries = [],
    )
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
    thread: BatchJobThread[MagicMock] = BatchJobThread(
      job          = job,
      stateRequest = RequestMetadata(),
      stateQueries = [],
    )
    # Execute test.
    result = thread.isJob(job = metadata)
    # Assert result.
    self.assertTrue(result)

  def testIsNotJob(self) -> None :
    """Test if the job can be identified."""
    # Prepare data.
    job = MagicMock()
    job.request.jobMetadata.id = 'job'
    thread: BatchJobThread[MagicMock] = BatchJobThread(
      job          = job,
      stateRequest = RequestMetadata(),
      stateQueries = [],
    )
    metadata    = ObjectMetadata()
    metadata.id = 'not-job'
    # Execute test.
    result = thread.isJob(job = metadata)
    # Assert result.
    self.assertFalse(result)
