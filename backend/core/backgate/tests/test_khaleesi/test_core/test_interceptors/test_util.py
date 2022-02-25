"""Test interceptor utility."""

# khaleesi.ninja.
from khaleesi.core.interceptors.util import Interceptor
from khaleesi.core.test_util.test_case import SimpleTestCase


class InterceptorTest(SimpleTestCase):
  """Test interceptor utility"""

  interceptor = Interceptor()

  def test_process_method_name(self) -> None :
    """Test the method name gets processed correctly."""
    for description, i_gate, i_service, i_grpc_service, i_grpc_method, raw in [
        ( 'full', 'gate', 'service', 'GrpcService', 'Method', '/khaleesi.gate.service.GrpcService/Method' ),  # pylint: disable=line-too-long
        ( 'no g service', 'gate', 'service', 'UNKNOWN', 'Method', '/khaleesi.gate.service/Method' ),
        ( 'no k service', 'gate', 'UNKNOWN', 'UNKNOWN', 'Method', '/khaleesi.gate/Method' ),
        ( 'no service', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Method', '/khaleesi/Method' ),
        ( 'no method', 'gate', 'service', 'GrpcService', 'UNKNOWN', '/khaleesi.gate.service.GrpcService/' ),  # pylint: disable=line-too-long
        ( 'empty input', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', '' ),
    ]:
      with self.subTest(case = description):
        # Execute test.
        o_gate, o_service, o_grpc_service, o_grpc_method = self.interceptor.process_method_name(
          raw = raw,
        )
        # Assert result.
        self.assertEqual(i_gate        , o_gate)
        self.assertEqual(i_service     , o_service)
        self.assertEqual(i_grpc_service, o_grpc_service)
        self.assertEqual(i_grpc_method , o_grpc_method)
