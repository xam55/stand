from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .models import EmailConfirmation


def send_confirmation_email(*, confirmation: EmailConfirmation) -> None:
    path = reverse("accounts:confirm", kwargs={"token": confirmation.token})
    send_mail(
        subject="Подтвердите email",
        message=f"Чтобы активировать аккаунт, перейдите по ссылке: {settings.SITE_URL}{path}",
        from_email=None,
        recipient_list=[confirmation.user.email],
    )
