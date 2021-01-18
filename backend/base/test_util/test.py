"""Add custom behavior to the DRF test cases."""

# Django.
from rest_framework.test import (
    APISimpleTestCase,
    APITestCase,
    APITransactionTestCase,
)


class TransactionTestCase(APITransactionTestCase):
  """Custom TestCase class for integration tests."""
  tags = {'integration'}
  databases = {'default', 'logging'}


class TestCase(APITestCase):
  """Custom TestCase class for integration tests."""
  tags = {'integration'}
  databases = {'default', 'logging'}


class SimpleTestCase(APISimpleTestCase):
  """Custom TestCase class for unit tests."""
  tags = {'unit'}


class CombinedTestCase(APISimpleTestCase):
  """Custom TestCase class combining unit and integration tests."""
  tags = {'unit', 'integration'}
