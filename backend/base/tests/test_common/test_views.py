"""Make sure that views override the required attributes."""

# khaleesi.ninja.
from test_util.test import CombinedTestCase
from common.views import View, GenericView


# noinspection PyUnresolvedReferences
class ViewTest(CombinedTestCase) :
  """Make sure that views override the required attributes."""

  def test_view(self) -> None :
    """Make sure that views override the required attributes."""
    with self.assertRaises(TypeError):
      View()  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated

  def test_generic_view(self) -> None :
    """Make sure that views override the required attributes."""
    with self.assertRaises(TypeError):
      GenericView()  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated
