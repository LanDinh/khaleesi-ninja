"""Test server interceptor utility."""

# Python.
from functools import partial
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.test_util import SimpleTestCase


class PrometheusServerInterceptorTest(SimpleTestCase):
  """Test PrometheusServerInterceptor"""

  interceptor = ServerInterceptor()

  def test_intercept(self) -> None :
    """Test the counter gets incremented."""
    for description, service, method, full_input in [
        ( 'full input', 'Service', 'Method', '/protobuf.package.Service/Method' ),
        ( 'empty service', 'UNKNOWN', 'Method', '//Method' ),
        ( 'empty method', 'Service', 'UNKNOWN', '/protobuf.package.Service/' ),
        ( 'empty input', 'UNKNOWN', 'UNKNOWN', '' ),
    ]:
      with self.subTest(case = description):
        # Prepare data.
        self.interceptor.khaleesi_intercept = partial(  # type: ignore[assignment]  # pylint: disable=line-too-long
          lambda inner_service, inner_method, **kwargs : self.assertEqual(
            (inner_service, inner_method),
            (kwargs['service_name'], kwargs['method_name'])
          ),
          inner_service = service,
          inner_method = method,
        )
        # Execute test & assert result.
        self.interceptor.intercept(
          method      = lambda *args: None,
          request     = MagicMock(),
          context     = MagicMock(),
          method_name = full_input,
        )
