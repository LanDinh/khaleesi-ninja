"""Test the mixin for job configuration."""

# Python.
from datetime import timedelta

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobConfiguration as GrpcJobConfiguration, Action
from tests.models import JobConfiguration as DbJobConfiguration


class JobConfigurationMixinTestCase(SimpleTestCase):
  """Test the mixin for job configuration."""

  def testJobConfigurationFromGrpc(self) -> None :
    """Test transforming to gRPC."""
    for cleanupIs in [ True, False ]:
      with self.subTest(cleanupConfiguration = cleanupIs):
        # Prepare data.
        instance = DbJobConfiguration()
        configuration = GrpcJobConfiguration()
        configuration.action.batchSize = 1337
        configuration.action.timelimit.FromTimedelta(timedelta(hours = 42))
        configuration.cleanup.isCleanupJob = cleanupIs
        configuration.cleanup.cleanupDelay.FromTimedelta(timedelta(minutes = 42))
        action = Action()
        action.site   = 'site'
        action.app    = 'app'
        action.action = 'action'
        # Execute test.
        instance.jobConfigurationFromGrpc(action = action, configuration = configuration)
        # Assert result.
        self._assert(instance = instance, action = action, configuration = configuration)

  def testJobConfigurationFromGrpcDefaultValues(self) -> None :
    """Test transforming to gRPC."""
    # Prepare data.
    instance = DbJobConfiguration()
    configuration = GrpcJobConfiguration()
    action = Action()
    action.site   = 'site'
    action.app    = 'app'
    action.action = 'action'
    # Execute test.
    instance.jobConfigurationFromGrpc(action = action, configuration = configuration)
    # Assert result.
    self.assertEqual(1000, instance.actionBatchSize)
    self.assertEqual(timedelta(hours = 1), instance.actionTimelimit)

  def testJobConfigurationToGrpc(self) -> None :
    """Test transforming to gRPC."""
    for cleanupIs in [ True, False ]:
      with self.subTest(cleanupConfiguration = cleanupIs):
        # Prepare data.
        instance = DbJobConfiguration()
        instance.actionBatchSize = 1337
        instance.actionTimelimit = timedelta(hours = 42)
        instance.cleanupIs       = cleanupIs
        instance.cleanupDelay    = timedelta(minutes = 42)
        configuration = GrpcJobConfiguration()
        action = Action()
        # Execute test.
        instance.jobConfigurationToGrpc(action = action, configuration = configuration)
        # Assert result.
        self._assert(instance = instance, action = action, configuration = configuration)

  def _assert(
      self, *,
      instance     : DbJobConfiguration,
      action       : Action,
      configuration: GrpcJobConfiguration,
  ) -> None :
    """Assert that the DB instance and gRPC forms are equivalent."""
    self.assertEqual(instance.site  , action.site)
    self.assertEqual(instance.app   , action.app)
    self.assertEqual(instance.action, action.action)
    self.assertEqual(instance.actionTimelimit, configuration.action.timelimit.ToTimedelta())
    self.assertEqual(instance.actionBatchSize, configuration.action.batchSize)
    self.assertEqual(instance.cleanupIs      , configuration.cleanup.isCleanupJob)
    self.assertEqual(instance.cleanupDelay   , configuration.cleanup.cleanupDelay.ToTimedelta())
