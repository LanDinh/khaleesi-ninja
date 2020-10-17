"""Base class for custom exceptions."""

# pylint: disable=line-too-long

# Python.
from typing import Any

# Django.
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict

# khaleesi.ninja.
# noinspection PyUnresolvedReferences,PyUnresolvedReferences
from translation.translate import translate as _


class KhaleesiException(Exception):
  """Base class for custom exceptions."""

  def __init__(self, code: int, data: Any) -> None :
    super().__init__(
        '{code}: {data}'.format(code = code, data = data.__str__()),
    )
    self.code = code
    self.data = data


class TeapotException(KhaleesiException):
  """Teapot - this should never have happened."""

  def __init__(self, *, data: Any) -> None :
    # noinspection PyUnresolvedReferences
    super().__init__(code = status.HTTP_418_IM_A_TEAPOT, data = data)  # type: ignore[attr-defined]


class PermissionDeniedException(KhaleesiException):
  """Permission denied."""

  def __init__(self) -> None :
    super().__init__(
        code = status.HTTP_403_FORBIDDEN,
        data = _('exception:user/authorization/denied'),
    )

class SerializerException(KhaleesiException):
  """Serializer exceptions."""

  def __init__(self, *, errors: ReturnDict) -> None :
    data = {}
    for key, messages in errors:
      data[key] = [
          _('exception:serializer/{code}'.format(code = message.code))
          for message in messages
      ]
    super().__init__(
        code = status.HTTP_400_BAD_REQUEST,
        data = data,
    )
