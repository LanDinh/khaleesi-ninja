"""Test basic job tracking."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.models import JobExecution
from khaleesi.proto.core_pb2 import JobExecutionResponse


class JobExecutionManagerTestCase(SimpleTestCase):
  """Test the job execution manager."""

  @patch('khaleesi.models.job.transaction.atomic')
  @patch.object(JobExecution.objects, 'filter')
  @patch.object(JobExecution.objects, 'create')
  def testStartJobExecution(
      self,
      create     : MagicMock,
      filterCount: MagicMock,
      *_         : MagicMock,
  ) -> None :
    """Test starting a job execution."""
    for count in [ 0, 1 ]:
      with self.subTest(count = count):
        # Prepare data.
        create.reset_mock()
        filterCount.reset_mock()
        filterCount.return_value.count.return_value = count
        # Execute test.
        JobExecution.objects.startJobExecution(job = MagicMock())
        # Assert result.
        create.assert_called_once()

  @patch('khaleesi.models.job.threading_enumerate')
  @patch.object(JobExecution.objects, 'filter')
  def testStopJobExecution(
      self,
      filterData        : MagicMock,
      threadingEnumerate: MagicMock,
  ) -> None :
    """Test stopping a job execution."""
    # Prepare data.
    job = MagicMock()
    job.jobId = 'job-id'
    filterData.return_value = [ job, job ]
    threadToStop = MagicMock()
    threadToStop.isBatchJobThread  = True
    threadToStop.isJob.side_effect = [ True, False ]
    threadToNotStop = MagicMock([ 'stop' ])
    threadingEnumerate.return_value = [ threadToStop, threadToNotStop ]
    # Execute test.
    JobExecution.objects.stopJob(idMessage = MagicMock())
    # Assert result.
    threadToStop.stop.assert_called_once()
    threadToNotStop.stop.assert_not_called()

  @patch('khaleesi.models.job.threading_enumerate')
  def testStopAllJobs(self, threadingEnumerate: MagicMock) -> None :
    """Test stopping a job execution."""
    # Prepare data.
    threadToStop = MagicMock()
    threadToStop.isBatchJobThread = True
    threadToStop.isJob              = True
    threadToNotStop = MagicMock([ 'stop' ])
    threadingEnumerate.return_value = [ threadToStop, threadToNotStop ]
    # Execute test.
    result = JobExecution.objects.stopAllJobs()
    # Assert result.
    threadToStop.stop.assert_called_once()
    threadToNotStop.stop.assert_not_called()
    self.assertEqual([ threadToStop ], result)


class JobExecutionTestCase(SimpleTestCase):
  """Test job executions."""

  def testInProgress(self) -> None :
    """Test if a job execution is in progress."""
    # Prepare data.
    jobExecution = JobExecution(status = 'IN_PROGRESS')
    # Execute test.
    result = jobExecution.inProgress
    # Assert result.
    self.assertTrue(result)

  def testNotInProgress(self) -> None :
    """Test if a job execution is in progress."""
    for statusLabel, statusType in [
        (statusLabel, statusType)
        for statusLabel, statusType in JobExecutionResponse.Status.items()
        if statusType != JobExecutionResponse.Status.IN_PROGRESS
    ]:
      with self.subTest(status = statusLabel):
        # Prepare data.
        jobExecution = JobExecution(status = statusLabel)
        # Execute test.
        result = jobExecution.inProgress
        # Assert result.
        self.assertFalse(result)

  def testSetTotal(self) -> None :
    """Test if a job execution is in progress."""
    # Prepare data.
    jobExecution = JobExecution()
    jobExecution.save = MagicMock()  # type: ignore[assignment]
    total = 13
    # Execute test.
    jobExecution.setTotal(total = 13)
    # Assert result.
    self.assertEqual(total, jobExecution.totalItems)
    jobExecution.save.assert_called_once_with()

  def testFinish(self) -> None :
    """Test finishing a job."""
    itemsProcessed = 13
    details        = 'details'
    for statusLabel, statusType in JobExecutionResponse.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        jobExecution = JobExecution()
        jobExecution.save = MagicMock()  # type: ignore[assignment]
        # Execute test.
        jobExecution.finish(
          status         = statusType,
          itemsProcessed = itemsProcessed,
          details        = details,
        )
        # Assert result.
        self.assertEqual(statusLabel   , jobExecution.status)
        self.assertEqual(itemsProcessed, jobExecution.itemsProcessed)
        self.assertEqual(details       , jobExecution.details)
        jobExecution.save.assert_called_once_with()

  @patch('khaleesi.models.job.addRequestMetadata')
  def testToGrpc(self, metadata: MagicMock) -> None :
    """Test transforming a job execution into a grpc request."""
    for statusLabel, statusType in JobExecutionResponse.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        metadata.reset_mock()
        jobExecution = JobExecution(
          jobId          = 'job-id',
          executionId    = 13,
          status         = statusLabel,
          itemsProcessed = 42,
          totalItems     = 1337,
          details        = 'details',
          end            = datetime.now().replace(tzinfo = timezone.utc)
        )
        # Execute test.
        result = jobExecution.toGrpc()
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(jobExecution.jobId         , result.executionMetadata.jobId)
        self.assertEqual(jobExecution.executionId   , result.executionMetadata.executionId)
        self.assertEqual(statusType                 , result.status)
        self.assertEqual(jobExecution.itemsProcessed, result.itemsProcessed)
        self.assertEqual(jobExecution.totalItems    , result.totalItems)
        self.assertEqual(jobExecution.details       , result.details)
        self.assertEqual(jobExecution.end, result.end.ToDatetime().replace(tzinfo = timezone.utc))
