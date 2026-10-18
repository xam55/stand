from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .cache import invalidate_women_list
from .models import Women


@receiver([post_save, post_delete], sender=Women)
def invalidate_women_cache(sender, **kwargs) -> None:
    transaction.on_commit(invalidate_women_list)
