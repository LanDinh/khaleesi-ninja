"""Channel Manager."""

# Python.
from typing import Dict

# Django.
from django.conf import settings

# gRPC.
import grpc

# khaleesi.ninja.
from khaleesi.core.interceptors.client.logging import LoggingClientInterceptor
from khaleesi.core.interceptors.client.prometheus import PrometheusClientInterceptor
from khaleesi.core.settings.definition import KhaleesiNinjaSettings


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class ChannelManager:
  """Channel manager."""

  channels: Dict[str, grpc.Channel]

  def __init__(self) -> None :
    self.channels = {}

  def get_channel(self, *, gate: str, service: str) -> grpc.Channel :
    """Get the named channel. If it doesn't exist yet, it is opened."""
    address = f'{gate}-{service}'
    port = khaleesi_settings["GRPC"]["PORT"]
    if not address in self.channels:
      channel = grpc.insecure_channel(f'{address}:{port}')
      interceptors = [
          PrometheusClientInterceptor(),
          LoggingClientInterceptor(),
      ]
      self.channels[address] = grpc.intercept_channel(channel, *interceptors)
    return self.channels[address]

  def close_all_channels(self) -> None :
    """Close all channels to clean up."""
    for _, value in self.channels.items():
      value.close()


CHANNEL_MANAGER = ChannelManager()
