"""Test the UpdateJobExecutionState batch job."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.job import JobTestMixin
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import (
  JobExecution as GrpcJobExecution, JobExecutionList,
  ObjectMetadata,
)
from microservice.batch.updateJobExecutionState import UpdateExecutionStateJob


@patch('khaleesi.core.batch.job.Paginator')
@patch('microservice.batch.updateJobExecutionState.JobExecution.objects.getJobExecutionsInProgress')
@patch('microservice.batch.updateJobExecutionState.MaidStub')
@patch('microservice.batch.updateJobExecutionState.SINGLETON')
class UpdateJobExecutionStateTestCase(JobTestMixin, SimpleTestCase):
  """Test the UpdateJobExecutionState batch job."""

  def testInit(self, singleton: MagicMock, stub: MagicMock, *_: MagicMock) -> None :
    """Test initializing the job."""
    # Execute test.
    job = UpdateExecutionStateJob(action = MagicMock(), request = self.buildCleanupRequest())
    # Assert result.
    self.assertIsNotNone(job.action)
    self.assertIsNotNone(job.httpRequestId)
    self.assertIsNotNone(job.stub)
    self.assertFalse(hasattr(job, 'grpcRequestId'))
    singleton.structuredLogger.logHttpRequest.assert_called_once()
    stub.assert_called_once()

  @patch('microservice.batch.updateJobExecutionState.transaction')
  @patch('microservice.batch.updateJobExecutionState.JobExecution.objects.bulk_update')
  def testExecuteBatch(self, bulkUpdate: MagicMock, *_: MagicMock) -> None :
    """Test executing a single batch."""
    # Prepare data.
    khaleesiId = 'id'
    job = UpdateExecutionStateJob(action = MagicMock(), request = self.buildCleanupRequest())
    fetchedJobExecutionStates = JobExecutionList()
    fetchedJobExecutionStates.jobExecutions.append(GrpcJobExecution())
    fetchedJobExecutionStates.jobExecutions[0].executionMetadata.id = khaleesiId
    job.getUpdatedJobExecutionState = MagicMock(return_value = fetchedJobExecutionStates)  # type: ignore[method-assign]  # pylint: disable=line-too-long
    page = MagicMock()
    page.object_list = [ MagicMock() ]
    page.object_list[0].khaleesiId = khaleesiId
    # Execute test.
    job.executeBatch(page = page)
    # Assert result.
    bulkUpdate.assert_called_once()

  @patch(
    'microservice.batch.updateJobExecutionState.JobExecution.objects.getJobExecutionsInProgress',
  )
  def testGetQueryset(
      self,
      singleton : MagicMock,  # pylint: disable=unused-argument
      stub      : MagicMock,  # pylint: disable=unused-argument
      filterData: MagicMock,
      *_        : MagicMock,
  ) -> None :
    """Test the definition of the queryset."""
    # Prepare data.
    job = UpdateExecutionStateJob(action = MagicMock(), request = self.buildCleanupRequest())
    # Execute test.
    job.getQueryset()
    # Assert result.
    filterData.assert_called_once()

  def testFinishJob(self, singleton: MagicMock, *_: MagicMock) -> None :
    """Test finishing up the job."""
    for statusLabel, _ in GrpcJobExecution.Status.items():  # type: ignore[assignment]
      with self.subTest(status = statusLabel):
        # Prepare data.
        singleton.reset_mock()
        job = UpdateExecutionStateJob(action = MagicMock(), request = self.buildCleanupRequest())
        job.jobExecution = MagicMock()
        job.jobExecution.status = statusLabel
        # Execute test.
        job.finishJob()
        # Assert result.
        singleton.structuredLogger.logHttpResponse.assert_called_once()


  @patch('microservice.batch.updateJobExecutionState.addSystemRequestMetadata')
  def testGetUpdatedJobExecutionState(self, metadata: MagicMock, *_: MagicMock) -> None :
    """Test getting the updated versions of job executions."""
    # Prepare data.
    job = UpdateExecutionStateJob(action = MagicMock(), request = self.buildCleanupRequest())
    instances = { 'test': MagicMock() }
    instances['test'].toObjectMetadata.return_value = ObjectMetadata()
    # Execute test.
    job.getUpdatedJobExecutionState(instances = instances)  # type: ignore[arg-type]
    # Assert result.
    metadata.assert_called_once()
    job.stub.FetchExecutionState.assert_called_once()
