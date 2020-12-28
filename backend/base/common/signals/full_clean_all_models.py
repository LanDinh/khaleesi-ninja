"""Connect custom signals."""

# Python.
from typing import Any

# Django.
from django.db.models import Model
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, dispatch_uid = 'common.signals.full_clean_all_models')
def full_clean_all_models(instance: Model, **_: Any) -> None :
  """Make sure that full_clean is called for models."""
  instance.full_clean(validate_unique = False)
