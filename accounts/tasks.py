import logging

from celery import shared_task
import smtplib
from . import services
from .emails import send_confirmation_email
from .models import EmailConfirmation

logger = logging.getLogger(__name__)

@shared_task(
    queue="io",
    autoretry_for=(OSError,),
    max_retries=5,
    retry_backoff=60,
    retry_backoff_max=1800,
    retry_jitter=True,
)
def send_confirmation_email_task(confirmation_id: int) -> None:
    confirmation = EmailConfirmation.objects.select_related("user").filter(pk=confirmation_id).first()
    if confirmation is None:
        logger.info("Подтверждение #%s уже не нужно, письмо не отправляем", confirmation_id)
        return

    try:
        send_confirmation_email(confirmation=confirmation)
    except smtplib.SMTPRecipientsRefused:
        logger.warning("Адрес %s отклонён почтовым сервером", confirmation.user.email)
        return

    logger.info("Письмо подтверждения отправлено на %s", confirmation.user.email)



@shared_task(queue="io")
def delete_unconfirmed_users_task() -> None:
    deleted = services.delete_unconfirmed_users()
    logger.info("Удалено неподтверждённых аккаунтов: %s", deleted)
