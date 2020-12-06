"""Make sure that app configs override the required attributes."""

# pylint: disable=line-too-long

# khaleesi.ninja.
from test_util.test import CombinedTestCase
from common.app_config import AppConfig


class AppConfigTest(CombinedTestCase) :
  """Make sure that views override the required attributes."""

  def test_app_config(self) -> None :
    """Make sure that views override the required attributes."""
    with self.assertRaises(TypeError):
      # noinspection PyArgumentList,PyUnresolvedReferences
      AppConfig()  # type: ignore[abstract,call-arg]  # pylint: disable=abstract-class-instantiated,no-value-for-parameter
