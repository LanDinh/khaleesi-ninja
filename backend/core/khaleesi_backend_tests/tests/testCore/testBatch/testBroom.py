"""Test the structured logger."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.batch.broom import Broom, instantiateBroom
from khaleesi.core.testUtil.testCase import SimpleTestCase


class TestBroom(SimpleTestCase):
  """Test the structured gRPC logger."""

  broom = Broom()

  def testCleanup(self) -> None :
    """Test sending a log request."""
    # Execute test & assert result.
    self.broom.cleanup(jobExecutionRequest = MagicMock())


class BroomInstantiationTest(SimpleTestCase):
  """Test instantiation."""

  @patch('khaleesi.core.batch.broom.LOGGER')
  @patch('khaleesi.core.batch.broom.importSetting')
  def testInstantiation(self, importSetting: MagicMock, *_: MagicMock) -> None :
    """Test instantiation."""
    # Execute test.
    instantiateBroom()
    # Assert result.
    importSetting.assert_called_once()
