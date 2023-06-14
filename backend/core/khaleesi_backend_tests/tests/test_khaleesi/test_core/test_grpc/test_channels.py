"""Test the channel manager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.grpc.channels import ChannelManager, CHANNEL_MANAGER
from khaleesi.core.test_util.test_case import SimpleTestCase


class ChannelManagerTestCase(SimpleTestCase):
  """Test the channel manager."""

  @patch('khaleesi.core.grpc.channels.grpc.intercept_channel')
  @patch('khaleesi.core.grpc.channels.grpc.insecure_channel')
  def test_get_channel(self, insecure: MagicMock, intercept: MagicMock) -> None :
    """Test getting a channel."""
    # Prepare data.
    channel = MagicMock()
    insecure.return_value = channel
    intercept.return_value = channel
    gate = 'gate'
    service = 'service'
    with self.subTest(test = 'first access'):
      # Execute test.
      result = CHANNEL_MANAGER.get_channel(gate = gate, service = service)
      # Assert result.
      self.assertEqual(channel, result)
      insecure.assert_called_once_with(f'{gate}-{service}:8000')
      intercept.assert_called_once()
      self.assertEqual(channel, intercept.call_args.args[0])
    with self.subTest(test = 'second access'):
      # Prepare data.
      insecure.reset_mock()
      intercept.reset_mock()
      # Execute test.
      result = CHANNEL_MANAGER.get_channel(gate = gate, service = service)
      # Assert result.
      self.assertEqual(channel, result)
      insecure.assert_not_called()
      intercept.assert_not_called()

  def test_close_all_channels(self) -> None :
    """Test all channels get closed."""
    # Prepare data.
    channels = [ MagicMock(), MagicMock() ]
    CHANNEL_MANAGER.channels['first'] = channels[0]
    CHANNEL_MANAGER.channels['second'] = channels[1]
    # Execute test.
    CHANNEL_MANAGER.close_all_channels()
    # Assert result.
    for channel in channels:
      channel.close.assert_called_once_with()

  def test_instantiate(self) -> None :
    """Test instantiation."""
    # Execute test.
    ChannelManager()
