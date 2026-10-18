import time

from botocore.exceptions import ConnectionError as S3ConnectionError
from celery import shared_task
from celery.utils.time import get_exponential_backoff_interval
from django.db import OperationalError

from .images import process_photo
from .models import Women
from .reports import build_report, mark_report_failed

TEMPORARY_ERRORS = (OSError, S3ConnectionError, OperationalError)


@shared_task(bind=True, queue="cpu", max_retries=3)
def build_women_report_task(self, report_id: int) -> None:
    try:
        build_report(report_id=report_id)
    except TEMPORARY_ERRORS as error:
        if self.request.retries < self.max_retries:
            countdown = get_exponential_backoff_interval(
                factor=30, retries=self.request.retries, maximum=600, full_jitter=True
            )
            raise self.retry(exc=error, countdown=countdown)
        mark_report_failed(report_id=report_id, error=error)
        raise
    except Exception as error:
        mark_report_failed(report_id=report_id, error=error)
        raise


@shared_task(
    queue="cpu",
    autoretry_for=TEMPORARY_ERRORS,
    max_retries=5,
    retry_backoff=10,
    retry_backoff_max=600,
    retry_jitter=True,
)
def process_photo_task(woman_id: int) -> None:
    process_photo(woman_id=woman_id)



@shared_task(queue="io")
def generate_woman_report(woman_id:int)-> None:
    woman = Women.objects.get(pk=woman_id)
    time.sleep(5)
    print(f"Отчет по записи {woman.pk} <<{woman.title}>> готов")
    

@shared_task(queue="io")
def io_task(n: int) -> None:
    start = time.perf_counter()
    time.sleep(2)
    print(f"IO  #{n} готова за {time.perf_counter() - start:.2f}с")


@shared_task(queue="cpu")
def cpu_task(n: int) -> None:
    start = time.perf_counter()
    total = 0
    for i in range(20_000_000):
        total += i % 7
    print(f"CPU #{n} готова за {time.perf_counter() - start:.2f}с")



@shared_task(queue="io")
def women_stats() -> None:
    from django.db.models import Count

    from .models import Category

    stats = Category.objects.annotate(total=Count("women")).values_list("name", "total")
    for name, total in stats:
        print(f"[stats] {name}: {total}")







