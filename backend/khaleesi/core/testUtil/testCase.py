"""Test utility."""

# Django.
from django.test import (
  TransactionTestCase as DjangoTransactionTestCase,
  SimpleTestCase as DjangoSimpleTestCase,
)


class SimpleTestCase(DjangoSimpleTestCase):
  """Override the SimpleTestCase."""


class TransactionTestCase(DjangoTransactionTestCase):
  """Override the TransactionTestCase."""

  databases = { 'default' }
