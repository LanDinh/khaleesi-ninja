"""Test basic job tracking."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.models import JobExecution as DbJobExecution
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution


class JobExecutionManagerTestCase(SimpleTestCase):
  """Test the job execution manager."""

  @patch.object(DbJobExecution.objects, 'filter')
  def testCountJobExecutionsInProgress(self, filterCount: MagicMock) -> None :
    """Test counting how many executions are in progress for the job in question."""
    # Execute test.
    DbJobExecution.objects.countJobExecutionsInProgress(job = MagicMock())
    # Assert result.
    filterCount.assert_called_once()
    filterCount.return_value.count.assert_called_once()

  @patch.object(DbJobExecution.objects, 'filter')
  def testGetJobExecutionsInProgress(self, filterData: MagicMock) -> None :
    """Test getting all executions that are in progress for the job in question."""
    # Prepare data.
    job = MagicMock()
    job.jobId       = 'job-id'
    job.executionId = 'execution-id'
    filterData.return_value = [ job, job ]
    # Execute test.
    result = DbJobExecution.objects.getJobExecutionsInProgress(job = MagicMock())
    # Assert result.
    self.assertEqual(2, len(result))


class JobExecutionTestCase(SimpleTestCase):
  """Test job executions."""

  @patch('khaleesi.models.jobExecution.JobExecution.toGrpc')
  @patch('khaleesi.models.jobExecution.JobExecution.toObjectMetadata')
  @patch('khaleesi.models.jobExecution.JobExecution.khaleesiSave')
  def testSetTotal(self, save: MagicMock, toObjectMetadata: MagicMock, toGrpc: MagicMock) -> None :
    """Test if a job execution is in progress."""
    # Prepare data.
    jobExecution = DbJobExecution()
    # Execute test.
    jobExecution.setTotal(total = 13)
    # Assert result.
    toObjectMetadata.assert_called_once()
    toGrpc.assert_called_once()
    save.assert_called_once()

  @patch('khaleesi.models.jobExecution.JobExecution.toGrpc')
  @patch('khaleesi.models.jobExecution.JobExecution.toObjectMetadata')
  @patch('khaleesi.models.jobExecution.JobExecution.khaleesiSave')
  def testFinish(self, save: MagicMock, toObjectMetadata: MagicMock, toGrpc: MagicMock) -> None :
    """Test finishing a job."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        save.reset_mock()
        toObjectMetadata.reset_mock()
        toGrpc.reset_mock()
        jobExecution = DbJobExecution()
        # Execute test.
        jobExecution.finish(
          status         = statusType,
          itemsProcessed = 13,
          statusDetails  = 'details',
        )
        # Assert result.
        toObjectMetadata.assert_called_once()
        toGrpc.assert_called_once()
        save.assert_called_once()

  @patch.object(DbJobExecution, 'jobExecutionFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveNew(self, parent: MagicMock, jobExecution: MagicMock) -> None :
    """Test creating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = GrpcJobExecution()
    grpc.executionMetadata.id = 'execution-id'
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    jobExecution.assert_called_once()
    self.assertEqual(grpc.executionMetadata.id, instance.executionId)

  @patch.object(DbJobExecution, 'jobExecutionFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveInProgress(self, parent: MagicMock, jobExecution: MagicMock) -> None :
    """Test updating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    instance._state.adding = False  # pylint: disable=protected-access
    grpc = GrpcJobExecution()
    grpc.executionMetadata.id = 'execution-id'
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    jobExecution.assert_called_once()
    self.assertFalse(instance.executionId)

  @patch.object(DbJobExecution, 'jobExecutionToGrpc')
  def testToGrpc(self, jobExecution: MagicMock) -> None :
    """Test transforming a job execution into a grpc request."""
    # Prepare data.
    instance = DbJobExecution(executionId = 'execution-id')
    # Execute test.
    result = instance.toGrpc()
    # Assert result.
    jobExecution.assert_called_once()
    self.assertEqual(instance.executionId   , result.executionMetadata.id)
