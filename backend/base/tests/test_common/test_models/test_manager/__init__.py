"""Tests for the custom base manager."""

# khaleesi.ninja.
from test_util.apps import setup_test_app

# We need test-only models for these tests, so register this package as app.
setup_test_app(__package__, 'test_base_models_manager')
