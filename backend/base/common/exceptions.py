"""Base class for custom exceptions."""

# pylint: disable=line-too-long

# Python.
from typing import Any

# Django.
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict

# khaleesi.ninja.
from translation.translate import translate_exception as _


class KhaleesiException(Exception):
  """Base class for custom exceptions."""

  def __init__(self, *, code: int, data: Any) -> None :
    super().__init__(f'{code}: {str(data)}')
    self.code = code
    self.data = data


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class TeapotException(KhaleesiException):
  """Teapot - this should never have happened."""

  def __init__(self, *, data: Any) -> None :
    super().__init__(code = status.HTTP_418_IM_A_TEAPOT, data = data)  # type: ignore[attr-defined]

class TwinException(TeapotException):
  """Teapot - there should never be twins."""

  def __init__(self) -> None :
    super().__init__(data = _('data/twins'))

class ZeroTupletException(TeapotException):
  """Teapot - there should always be an object."""

  def __init__(self) -> None :
    super().__init__(data = _('data/zerotuplet'))


class SerializerException(KhaleesiException):
  """Serializer exceptions."""

  def __init__(self, *, errors: ReturnDict) -> None :
    data = {}
    for key, messages in errors:
      data[key] = [
          _(f'data/serializer/{message.code}') for message in messages
      ]
    super().__init__(
        code = status.HTTP_400_BAD_REQUEST,
        data = data,
    )


class PermissionDeniedException(KhaleesiException):
  """Permission denied."""

  def __init__(self) -> None :
    super().__init__(
        code = status.HTTP_403_FORBIDDEN,
        data = _('authorization/denied'),
    )
