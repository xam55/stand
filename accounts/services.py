from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from . import tasks
from .models import EmailConfirmation

User = get_user_model()

CONFIRMATION_TTL = timedelta(hours=24)


@transaction.atomic
def register_user(*, email: str, password: str) -> User:
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        is_active=False,
    )
    confirmation = EmailConfirmation.objects.create(user=user)
    transaction.on_commit(lambda: tasks.send_confirmation_email_task.delay(confirmation.pk))
    return user


@transaction.atomic
def resend_confirmation(*, email: str) -> None:
    confirmation = EmailConfirmation.objects.filter(
        user__username=email,
        user__is_active=False,
    ).first()
    if confirmation is None:
        return

    EmailConfirmation.objects.filter(pk=confirmation.pk).update(created_at=timezone.now())
    transaction.on_commit(lambda: tasks.send_confirmation_email_task.delay(confirmation.pk))


@transaction.atomic
def confirm_email(*, token) -> User:
    confirmation = EmailConfirmation.objects.select_related("user").get(token=token)
    user = confirmation.user
    user.is_active = True
    user.save(update_fields=["is_active"])
    confirmation.delete()
    return user


def delete_unconfirmed_users() -> int:
    deadline = timezone.now() - CONFIRMATION_TTL
    _, deleted_by_model = User.objects.filter(
        is_active=False,
        email_confirmation__created_at__lt=deadline,
    ).delete()
    return deleted_by_model.get(User._meta.label, 0)
