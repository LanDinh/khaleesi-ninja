"""Provide a custom JSON encoder for the settings.py"""

# Python.
from dataclasses import is_dataclass, asdict
from typing import Any

# Django.
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import renderers


class JSONEncoder(DjangoJSONEncoder):
  """Make it possible to encode dataclasses."""
  def default(self, o: Any) -> Any :
    """Make it possible to encode dataclasses."""
    if is_dataclass(o):
      return asdict(o)
    return super().default(o)


class JSONRenderer(renderers.JSONRenderer):
  """Define a renderer using my custom encoder."""
  encoder_class = JSONEncoder
