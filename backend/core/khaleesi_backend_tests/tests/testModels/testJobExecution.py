"""Test basic job tracking."""

# Python.
from datetime import datetime, timezone
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

  def testInProgress(self) -> None :
    """Test if a job execution is in progress."""
    # Prepare data.
    jobExecution = DbJobExecution(status = 'IN_PROGRESS')
    # Execute test.
    result = jobExecution.inProgress
    # Assert result.
    self.assertTrue(result)

  def testNotInProgress(self) -> None :
    """Test if a job execution is in progress."""
    for statusLabel, statusType in [
        (statusLabel, statusType)
        for statusLabel, statusType in GrpcJobExecution.Status.items()
        if statusType != GrpcJobExecution.Status.IN_PROGRESS
    ]:
      with self.subTest(status = statusLabel):
        # Prepare data.
        jobExecution = DbJobExecution(status = statusLabel)
        # Execute test.
        result = jobExecution.inProgress
        # Assert result.
        self.assertFalse(result)

  @patch('khaleesi.models.jobExecution.JobExecution.toGrpc')
  @patch('khaleesi.models.jobExecution.JobExecution.khaleesiSave')
  def testSetTotal(self, save: MagicMock, toGrpc: MagicMock) -> None :
    """Test if a job execution is in progress."""
    # Prepare data.
    jobExecution = DbJobExecution()
    # Execute test.
    jobExecution.setTotal(total = 13)
    # Assert result.
    toGrpc.assert_called_once()
    save.assert_called_once()

  @patch('khaleesi.models.jobExecution.JobExecution.toGrpc')
  @patch('khaleesi.models.jobExecution.JobExecution.khaleesiSave')
  def testFinish(self, save: MagicMock, toGrpc: MagicMock) -> None :
    """Test finishing a job."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        save.reset_mock()
        toGrpc.reset_mock()
        jobExecution = DbJobExecution()
        # Execute test.
        jobExecution.finish(
          status         = statusType,
          itemsProcessed = 13,
          statusDetails  = 'details',
        )
        # Assert result.
        toGrpc.assert_called_once()
        save.assert_called_once()

  @patch.object(DbJobExecution, 'jobConfigurationFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveNew(self, parent: MagicMock, jobConfiguration: MagicMock) -> None :
    """Test creating an instance from gRPC."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        instance = DbJobExecution()
        instance._state.adding = True  # pylint: disable=protected-access
        grpc = GrpcJobExecution()
        jobConfiguration.reset_mock()
        parent.reset_mock()
        # Relevant attributes.
        grpc.jobMetadata.id       = 'job-id'
        grpc.executionMetadata.id = 'execution-id'
        grpc.status               = statusType
        # Ignored attributes.
        grpc.end.FromDatetime(datetime.now(tz = timezone.utc))
        grpc.statusDetails  = 'details'
        grpc.itemsProcessed = 42
        # Execute test.
        instance.khaleesiSave(grpc = grpc)
        # Assert result.
        parent.assert_called_once()
        jobConfiguration.assert_called_once()
        self.assertEqual(grpc.jobMetadata.id      , instance.jobId)
        self.assertEqual(grpc.executionMetadata.id, instance.executionId)
        self.assertEqual(statusLabel              , instance.status)
        self.assertFalse(instance.end)
        self.assertFalse(instance.statusDetails)
        self.assertFalse(instance.totalItems)
        self.assertFalse(instance.itemsProcessed)

  @patch.object(DbJobExecution, 'jobConfigurationFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveInProgress(self, parent: MagicMock, jobConfiguration: MagicMock) -> None :
    """Test updating an instance from gRPC."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        parent.reset_mock()
        instance = DbJobExecution()
        instance._state.adding = False  # pylint: disable=protected-access
        instance.status = GrpcJobExecution.Status.Name(GrpcJobExecution.Status.IN_PROGRESS)
        grpc = GrpcJobExecution()
        # Ignored attributes.
        grpc.jobMetadata.id       = 'job-id'
        grpc.executionMetadata.id = 'execution-id'
        grpc.end.FromDatetime(datetime.now(tz = timezone.utc))
        # Relevant attributes.
        grpc.statusDetails  = 'details'
        grpc.itemsProcessed = 42
        grpc.status         = statusType
        # Execute test.
        instance.khaleesiSave(grpc = grpc)
        # Assert result.
        parent.assert_called_once()
        jobConfiguration.assert_not_called()
        self.assertFalse(instance.jobId)
        self.assertFalse(instance.executionId)
        self.assertFalse(instance.end)
        self.assertEqual(statusLabel        , instance.status)
        self.assertEqual(grpc.statusDetails , instance.statusDetails)
        self.assertEqual(grpc.itemsProcessed, instance.itemsProcessed)
        self.assertFalse(instance.totalItems)

  @patch.object(DbJobExecution, 'jobConfigurationFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveTotalItems(self, parent: MagicMock, *_: MagicMock) -> None :
    """Test updating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    grpc = GrpcJobExecution()
    grpc.totalItems = 1337
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    self.assertEqual(grpc.totalItems, instance.totalItems)

  @patch.object(DbJobExecution, 'jobConfigurationFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveDontOverwriteTotalItems(self, parent: MagicMock, *_: MagicMock) -> None :
    """Test updating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    instance.totalItems = 1337
    grpc = GrpcJobExecution()
    grpc.totalItems = 9000
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    self.assertNotEqual(grpc.totalItems, instance.totalItems)

  @patch.object(DbJobExecution, 'jobConfigurationToGrpc')
  @patch('khaleesi.models.jobExecution.Model.toGrpc')
  def testToGrpc(self, metadata: MagicMock, jobConfiguration: MagicMock) -> None :
    """Test transforming a job execution into a grpc request."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        metadata.reset_mock()
        metadata.return_value = GrpcJobExecution()
        jobConfiguration.reset_mock()
        jobExecution = DbJobExecution(
          jobId          = 'job-id',
          executionId    = 'execution-id',
          status         = statusLabel,
          end            = datetime.now().replace(tzinfo = timezone.utc),
          statusDetails  = 'details',
          itemsProcessed = 42,
          totalItems     = 1337,
        )
        # Execute test.
        result = jobExecution.toGrpc()
        # Assert result.
        metadata.assert_called_once()
        jobConfiguration.assert_called_once()
        self.assertEqual(jobExecution.jobId         , result.jobMetadata.id)
        self.assertEqual(jobExecution.executionId   , result.executionMetadata.id)
        self.assertEqual(statusType                 , result.status)
        self.assertEqual(jobExecution.end, result.end.ToDatetime().replace(tzinfo = timezone.utc))
        self.assertEqual(jobExecution.statusDetails , result.statusDetails)
        self.assertEqual(jobExecution.itemsProcessed, result.itemsProcessed)
        self.assertEqual(jobExecution.totalItems    , result.totalItems)
