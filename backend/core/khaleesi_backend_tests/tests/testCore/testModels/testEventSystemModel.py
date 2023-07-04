"""Test the khaleesi base model event sending."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from tests.models.eventSystemModel import EventSystemModel


@patch('khaleesi.core.models.eventSystemModel.SINGLETON')
class ModelManagerTestCase(SimpleTestCase):
  """Test the khaleesi base model event sending."""

  @patch('khaleesi.core.models.eventSystemModel.BaseModelManager.khaleesiCreate')
  def testKhaleesiCreate(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    instance = MagicMock()
    instance.khaleesiCreated  = datetime.now(tz = timezone.utc)
    instance.khaleesiModified = datetime.now(tz = timezone.utc)
    parent.return_value = instance
    # Execute test.
    EventSystemModel.objects.khaleesiCreate(grpc = MagicMock())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventSystemModel.BaseModelManager.khaleesiCreate')
  def testKhaleesiCreateError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    parent.side_effect = Exception()
    # Execute test.
    with self.assertRaises(Exception):
      EventSystemModel.objects.khaleesiCreate(grpc = MagicMock())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventSystemModel.BaseModelManager.khaleesiUpdate')
  def testKhaleesiUpdate(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    instance = MagicMock()
    instance.khaleesiCreated  = datetime.now(tz = timezone.utc)
    instance.khaleesiModified = datetime.now(tz = timezone.utc)
    parent.return_value = instance
    # Execute test.
    EventSystemModel.objects.khaleesiUpdate(metadata = MagicMock(), grpc = MagicMock())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventSystemModel.BaseModelManager.khaleesiUpdate')
  def testKhaleesiUpdateError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    parent.side_effect = Exception()
    # Execute test.
    with self.assertRaises(Exception):
      EventSystemModel.objects.khaleesiUpdate(metadata = MagicMock(), grpc = MagicMock())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventSystemModel.BaseModelManager.khaleesiDelete')
  def testKhaleesiDelete(self, _: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Execute test.
    EventSystemModel.objects.khaleesiDelete(metadata = MagicMock())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventSystemModel.BaseModelManager.khaleesiDelete')
  def testKhaleesiDeleteError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    parent.side_effect = Exception()
    # Execute test.
    with self.assertRaises(Exception):
      EventSystemModel.objects.khaleesiDelete(metadata = MagicMock())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()