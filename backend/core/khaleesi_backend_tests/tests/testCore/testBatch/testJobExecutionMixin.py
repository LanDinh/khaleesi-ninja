"""Test basic job tracking."""

# Python.
from datetime import datetime, timezone

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution
from tests.models.jobExecution import JobExecution as DbJobExecution


class JobExecutionMixinTestCase(SimpleTestCase):
  """Test job executions."""

  def testInProgress(self) -> None :
    """Test if a job execution is in progress."""
    for status in [ 'IN_PROGRESS', 'SCHEDULED' ]:
      with self.subTest(status = status):
        # Prepare data.
        jobExecution = DbJobExecution(status = status)
        # Execute test.
        result = jobExecution.inProgress
        # Assert result.
        self.assertTrue(result)

  def testNotInProgress(self) -> None :
    """Test if a job execution is in progress."""
    for statusLabel, statusType in [
        (statusLabel, statusType)
        for statusLabel, statusType in GrpcJobExecution.Status.items()
        if not statusType in [
            GrpcJobExecution.Status.IN_PROGRESS,
            GrpcJobExecution.Status.SCHEDULED,
        ]
    ]:
      with self.subTest(status = statusLabel):
        # Prepare data.
        jobExecution = DbJobExecution(status = statusLabel)
        # Execute test.
        result = jobExecution.inProgress
        # Assert result.
        self.assertFalse(result)

  def testJobExecutionFromGrpcNew(self) -> None :
    """Test creating an instance from gRPC."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        instance = DbJobExecution()
        instance._state.adding = True  # pylint: disable=protected-access
        grpc = GrpcJobExecution()
        # Relevant attributes.
        grpc.jobMetadata.id = 'job-id'
        grpc.status         = statusType
        # Ignored attributes.
        grpc.end.FromDatetime(datetime.now(tz = timezone.utc))
        grpc.statusDetails  = 'details'
        grpc.itemsProcessed = 42
        # Execute test.
        instance.jobExecutionFromGrpc(grpc = grpc)
        # Assert result.
        self.assertEqual(grpc.jobMetadata.id, instance.jobId)
        self.assertEqual(statusLabel        , instance.status)
        self.assertFalse(instance.end)
        self.assertFalse(instance.statusDetails)
        self.assertFalse(instance.totalItems)
        self.assertFalse(instance.itemsProcessed)

  def testJobExecutionFromGrpcInProgress(self) -> None :
    """Test updating an instance from gRPC."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        instance = DbJobExecution()
        instance._state.adding = False  # pylint: disable=protected-access
        instance.status = GrpcJobExecution.Status.Name(GrpcJobExecution.Status.IN_PROGRESS)
        grpc = GrpcJobExecution()
        # Ignored attributes.
        grpc.jobMetadata.id       = 'job-id'
        grpc.end.FromDatetime(datetime.now(tz = timezone.utc))
        # Relevant attributes.
        grpc.statusDetails  = 'details'
        grpc.itemsProcessed = 42
        grpc.status         = statusType
        # Execute test.
        instance.jobExecutionFromGrpc(grpc = grpc)
        # Assert result.
        self.assertFalse(instance.jobId)
        self.assertFalse(instance.end)
        self.assertEqual(statusLabel        , instance.status)
        self.assertEqual(grpc.statusDetails , instance.statusDetails)
        self.assertEqual(grpc.itemsProcessed, instance.itemsProcessed)
        self.assertFalse(instance.totalItems)

  def testJobExecutionFromGrpcTotalItems(self) -> None :
    """Test updating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    grpc = GrpcJobExecution()
    grpc.totalItems = 1337
    # Execute test.
    instance.jobExecutionFromGrpc(grpc = grpc)
    # Assert result.
    self.assertEqual(grpc.totalItems, instance.totalItems)

  def testJobExecutionFromGrpcDontOverwriteTotalItems(self) -> None :
    """Test updating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    instance.totalItems = 1337
    grpc = GrpcJobExecution()
    grpc.totalItems = 9000
    # Execute test.
    instance.jobExecutionFromGrpc(grpc = grpc)
    # Assert result.
    self.assertNotEqual(grpc.totalItems, instance.totalItems)

  def testJobExecutionToGrpc(self) -> None :
    """Test transforming a job execution into a grpc request."""
    for statusLabel, statusType in GrpcJobExecution.Status.items():
      with self.subTest(status = statusLabel):
        # Prepare data.
        jobExecution = DbJobExecution(
          jobId          = 'job-id',
          status         = statusLabel,
          end            = datetime.now().replace(tzinfo = timezone.utc),
          statusDetails  = 'details',
          itemsProcessed = 42,
          totalItems     = 1337,
        )
        # Execute test.
        result = jobExecution.jobExecutionToGrpc()
        # Assert result.
        self.assertEqual(jobExecution.jobId, result.jobMetadata.id)
        self.assertEqual(statusType        , result.status)
        self.assertEqual(jobExecution.end, result.end.ToDatetime().replace(tzinfo = timezone.utc))
        self.assertEqual(jobExecution.statusDetails , result.statusDetails)
        self.assertEqual(jobExecution.itemsProcessed, result.itemsProcessed)
        self.assertEqual(jobExecution.totalItems    , result.totalItems)
