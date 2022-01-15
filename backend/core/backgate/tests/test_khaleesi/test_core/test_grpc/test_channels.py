"""Test the channel manager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.grpc.channels import ChannelManager
from khaleesi.core.test_util import SimpleTestCase


class ChannelManagerTestCase(SimpleTestCase):
  """Test the channel manager."""

  @patch('khaleesi.core.grpc.channels.grpc.insecure_channel')
  def test_get_channel(self, grpc_channel: MagicMock) -> None :
    """Test getting a channel."""
    # Prepare data.
    channel_manager = ChannelManager()
    channel = MagicMock()
    grpc_channel.return_value = channel
    gate = 'gate'
    service = 'service'
    with self.subTest(test = 'first access'):
      # Execute test.
      result = channel_manager.get_channel(gate = gate, service = service)
      # Assert result.
      self.assertEqual(channel, result)
      grpc_channel.assert_called_once_with(f'{gate}-{service}:8000')
    with self.subTest(test = 'second access'):
      # Prepare data.
      grpc_channel.reset_mock()
      # Execute test.
      result = channel_manager.get_channel(gate = gate, service = service)
      # Assert result.
      self.assertEqual(channel, result)
      grpc_channel.assert_not_called()

  def test_close_all_channels(self) -> None :  # pylint: disable=no-self-use
    """Test all channels get closed."""
    # Prepare data.
    channel_manager = ChannelManager()
    channels = [ MagicMock(), MagicMock() ]
    channel_manager.channels['first'] = channels[0]
    channel_manager.channels['second'] = channels[1]
    # Execute test.
    channel_manager.close_all_channels()
    # Assert result.
    for channel in channels:
      channel.close.assert_called_once_with()
