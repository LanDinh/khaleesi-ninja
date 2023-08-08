"""Test basic job tracking."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecution as GrpcJobExecution
from microservice.models.jobExecution import JobExecution as DbJobExecution


class JobExecutionTestCase(SimpleTestCase):
  """Test job executions."""

  @patch.object(DbJobExecution, 'jobExecutionFromGrpc')
  @patch.object(DbJobExecution, 'jobConfigurationFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveNew(
      self,
      parent          : MagicMock,
      jobConfiguration: MagicMock,
      jobExecution    : MagicMock,
  ) -> None :
    """Test creating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = GrpcJobExecution()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    jobConfiguration.assert_called_once()
    jobExecution.assert_called_once()
    self.assertEqual(
      GrpcJobExecution.Status.Name(GrpcJobExecution.Status.SCHEDULED),
      instance.status,
    )

  @patch.object(DbJobExecution, 'jobExecutionFromGrpc')
  @patch.object(DbJobExecution, 'jobConfigurationFromGrpc')
  @patch('khaleesi.models.jobExecution.Model.khaleesiSave')
  def testSaveInProgress(
      self,
      parent          : MagicMock,
      jobConfiguration: MagicMock,
      jobExecution    : MagicMock,
  ) -> None :
    """Test updating an instance from gRPC."""
    # Prepare data.
    instance = DbJobExecution()
    instance._state.adding = False  # pylint: disable=protected-access
    grpc = GrpcJobExecution()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    jobConfiguration.assert_not_called()
    jobExecution.assert_called_once()
    self.assertNotEqual(
      GrpcJobExecution.Status.SCHEDULED,
      GrpcJobExecution.Status.Value(instance.status),
    )

  @patch.object(DbJobExecution, 'toObjectMetadata')
  @patch.object(DbJobExecution, 'jobExecutionToGrpc')
  @patch.object(DbJobExecution, 'jobConfigurationToGrpc')
  def testToGrpc(
      self,
      jobConfiguration: MagicMock,
      jobExecution    : MagicMock,
      objectMetadata  : MagicMock,
  ) -> None :
    """Test transforming a job execution into a grpc request."""
    # Prepare data.
    instance = DbJobExecution(start = datetime.now(tz = timezone.utc))
    # Execute test.
    result = instance.toGrpc()
    # Assert result.
    jobConfiguration.assert_called_once()
    jobExecution.assert_called_once()
    objectMetadata.assert_called_once()
    result.start.FromDatetime.assert_called_once()  # type: ignore[attr-defined]
    result.executionMetadata.CopyFrom.assert_called_once()  # type: ignore[attr-defined]
