"""Test the actuator."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import (
  JobExecutionMetadata,
  JobActionConfiguration,
  JobCleanupActionConfiguration,
)
from microservice.actuator.actuator import ACTUATOR


class ActuatorTest(SimpleTestCase):
  """Test the actuator."""

  def test_actuate_wrong_action_name_format(self) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    with self.assertRaises(InvalidArgumentException) as exception:
      # Execute test.
      ACTUATOR.actuate(
        action_name = 'invalid-name',
        job         = MagicMock(),
        action      = MagicMock(),
        cleanup     = MagicMock(),
      )
      # Assert result.
      self.assertIn('wrong format', exception.exception.private_message)

  def test_actuate_unknown_action(self) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    with self.assertRaises(InvalidArgumentException) as exception:
      # Execute test.
      ACTUATOR.actuate(
        action_name = 'unknown.action.name',
        job         = MagicMock(),
        action      = MagicMock(),
        cleanup     = MagicMock(),
      )
      # Assert result.
      self.assertIn('exists', exception.exception.private_message)

  def test_actuate(self) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    # Prepare data.
    mock = MagicMock()
    # Execute test.
    with patch.dict('microservice.actuator.actuator.CORE', { 'some': { 'action': mock } }):
      ACTUATOR.actuate(
        action_name = 'core.some.action',
        job         = JobExecutionMetadata(),
        action      = JobActionConfiguration(),
        cleanup     = JobCleanupActionConfiguration(),
      )
    # Assert result.
    mock.assert_called_once()
