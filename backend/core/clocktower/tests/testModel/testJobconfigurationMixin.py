"""Test the mixin for job configuration."""

# Python.
from datetime import timedelta

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobActionConfiguration, JobCleanupActionConfiguration
from tests.models import JobConfiguration


class JobConfigurationMixinTestCase(SimpleTestCase):
  """Test the mixin for job configuration."""

  def testJobConfigurationFromGrpc(self) -> None :
    """Test transforming to gRPC."""
    for cleanupIs in [ True, False ]:
      with self.subTest(cleanupConfiguration = cleanupIs):
        # Prepare data.
        instance = JobConfiguration()
        action = JobActionConfiguration()
        action.batchSize = 1337
        action.timelimit.FromTimedelta(timedelta(hours = 42))
        cleanup = JobCleanupActionConfiguration()
        cleanup.isCleanupJob = cleanupIs
        cleanup.cleanupDelay.FromTimedelta(timedelta(minutes = 42))
        # Execute test.
        instance.jobConfigurationFromGrpc(action = action, cleanup = cleanup)
        # Assert result.
        self._assert(instance = instance, action = action, cleanup = cleanup)

  def testJobConfigurationFromGrpcDefaultValues(self) -> None :
    """Test transforming to gRPC."""
    # Prepare data.
    instance = JobConfiguration()
    action = JobActionConfiguration()
    cleanup = JobCleanupActionConfiguration()
    # Execute test.
    instance.jobConfigurationFromGrpc(action = action, cleanup = cleanup)
    # Assert result.
    self.assertEqual(1000, instance.actionBatchSize)
    self.assertEqual(timedelta(hours = 1), instance.actionTimelimit)

  def testJobConfigurationToGrpc(self) -> None :
    """Test transforming to gRPC."""
    for cleanupIs in [ True, False ]:
      with self.subTest(cleanupConfiguration = cleanupIs):
        # Prepare data.
        instance = JobConfiguration()
        instance.actionBatchSize = 1337
        instance.actionTimelimit = timedelta(hours = 42)
        instance.cleanupIs       = cleanupIs
        instance.cleanupDelay    = timedelta(minutes = 42)
        action  = JobActionConfiguration()
        cleanup = JobCleanupActionConfiguration()
        # Execute test.
        instance.jobConfigurationToGrpc(action = action, cleanup = cleanup)
        # Assert result.
        self._assert(instance = instance, action = action, cleanup = cleanup)

  def _assert(
      self, *,
      instance: JobConfiguration,
      action  : JobActionConfiguration,
      cleanup : JobCleanupActionConfiguration,
  ) -> None :
    """Assert that the DB instance and gRPC forms are equivalent."""
    self.assertEqual(instance.actionTimelimit, action.timelimit.ToTimedelta())
    self.assertEqual(instance.actionBatchSize, action.batchSize)
    self.assertEqual(instance.cleanupIs      , cleanup.isCleanupJob)
    self.assertEqual(instance.cleanupDelay   , cleanup.cleanupDelay.ToTimedelta())
